#!/usr/bin/env python3
"""
FramePrep - Web-to-Samsung-Frame Image Prep Tool

Processes images from URLs (direct images or webpages) for Samsung Frame TV.
Outputs images at 3840×2160 (16:9) with optimal quality.
"""

import argparse
import json
import logging
import os
import re
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from urllib.parse import urljoin, urlparse, urlunparse

import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageOps

try:
    import imagehash
    HAS_IMAGEHASH = True
except ImportError:
    HAS_IMAGEHASH = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


class ImageCandidate:
    """Represents a candidate image URL with metadata."""

    def __init__(self, url: str, width: Optional[int] = None,
                 height: Optional[int] = None, source: str = "img"):
        self.url = url
        self.width = width
        self.height = height
        self.source = source  # Where it came from: img, srcset, og:image, etc.
        self.score = 0

    def calculate_score(self):
        """Calculate a priority score for this candidate."""
        score = 0

        # Dimension-based scoring
        if self.width and self.height:
            score += self.width * self.height
        elif self.width:
            score += self.width * 1000  # Assume reasonable height
        elif self.height:
            score += self.height * 1000  # Assume reasonable width
        else:
            score += 1000000  # Unknown size, give medium priority

        # Source-based bonuses
        if self.source in ['og:image', 'twitter:image']:
            score += 500000  # Social meta tags often point to hero images
        elif self.source == 'srcset':
            score += 200000  # Srcset usually has hi-res versions

        # Penalties for likely thumbnails/icons
        url_lower = self.url.lower()
        if any(keyword in url_lower for keyword in ['thumb', 'icon', 'sprite', 'avatar', 'logo']):
            score -= 1000000

        # Penalties for certain formats
        if url_lower.endswith('.gif'):
            score -= 500000
        if url_lower.endswith('.svg'):
            score -= 1000000  # SVG not suitable for Frame

        self.score = score
        return score

    def __repr__(self):
        return f"ImageCandidate(url={self.url[:50]}..., width={self.width}, height={self.height}, score={self.score})"


class FramePrep:
    """Main FramePrep application."""

    def __init__(self, args):
        self.args = args
        self.output_dir = Path(args.out)
        self.tmp_dir = Path(args.tmp)
        self.target_width, self.target_height = map(int, args.target.split('x'))
        self.target_aspect = self.target_width / self.target_height

        # Create directories
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.tmp_dir.mkdir(parents=True, exist_ok=True)

        # Tracking
        self.downloaded_urls: Set[str] = set()
        self.processed_hashes: Set[str] = set()
        self.manifest: List[Dict] = []
        self.stats = {
            'page_type': 'unknown',
            'candidates_found': 0,
            'images_downloaded': 0,
            'images_processed': 0,
            'images_skipped': 0,
            'errors': 0
        }

        # Session with retry logic
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })

    def is_direct_image_url(self, url: str) -> bool:
        """Check if URL points directly to an image."""
        # Check extension first (fast)
        parsed = urlparse(url)
        path_lower = parsed.path.lower()
        image_extensions = {'.jpg', '.jpeg', '.png', '.webp', '.tif', '.tiff', '.bmp'}

        if any(path_lower.endswith(ext) for ext in image_extensions):
            return True

        # Try HEAD request to check Content-Type
        try:
            response = self.session.head(url, timeout=10, allow_redirects=True)
            content_type = response.headers.get('Content-Type', '').lower()
            if content_type.startswith('image/'):
                return True
        except requests.RequestException:
            # HEAD might be blocked, try GET with stream
            try:
                response = self.session.get(url, timeout=10, stream=True, allow_redirects=True)
                content_type = response.headers.get('Content-Type', '').lower()
                response.close()
                if content_type.startswith('image/'):
                    return True
            except requests.RequestException:
                pass

        return False

    def extract_image_candidates(self, html: str, page_url: str) -> List[ImageCandidate]:
        """Extract all image candidates from HTML."""
        candidates = []
        soup = BeautifulSoup(html, 'lxml')

        # 1. Extract from <img> tags
        for img in soup.find_all('img'):
            # Check srcset first
            srcset = img.get('srcset', '')
            if srcset:
                # Parse srcset: "url1 width1, url2 width2, ..."
                entries = [s.strip() for s in srcset.split(',')]
                for entry in entries:
                    parts = entry.split()
                    if len(parts) >= 2:
                        url = parts[0]
                        descriptor = parts[1]
                        width = None
                        if descriptor.endswith('w'):
                            try:
                                width = int(descriptor[:-1])
                            except ValueError:
                                pass
                        candidates.append(ImageCandidate(
                            urljoin(page_url, url),
                            width=width,
                            source='srcset'
                        ))

            # Regular src
            src = img.get('src', '')
            if src and not src.startswith('data:'):
                width = None
                height = None
                try:
                    if img.get('width'):
                        width = int(img['width'])
                    if img.get('height'):
                        height = int(img['height'])
                except (ValueError, TypeError):
                    pass

                candidates.append(ImageCandidate(
                    urljoin(page_url, src),
                    width=width,
                    height=height,
                    source='img'
                ))

        # 2. Extract from <picture><source> tags
        for picture in soup.find_all('picture'):
            for source in picture.find_all('source'):
                srcset = source.get('srcset', '')
                if srcset:
                    entries = [s.strip() for s in srcset.split(',')]
                    for entry in entries:
                        parts = entry.split()
                        if parts:
                            url = parts[0]
                            width = None
                            if len(parts) >= 2 and parts[1].endswith('w'):
                                try:
                                    width = int(parts[1][:-1])
                                except ValueError:
                                    pass
                            candidates.append(ImageCandidate(
                                urljoin(page_url, url),
                                width=width,
                                source='picture'
                            ))

        # 3. OpenGraph image
        og_image = soup.find('meta', property='og:image')
        if og_image and og_image.get('content'):
            candidates.append(ImageCandidate(
                urljoin(page_url, og_image['content']),
                source='og:image'
            ))

        # 4. Twitter card image
        twitter_image = soup.find('meta', attrs={'name': 'twitter:image'})
        if twitter_image and twitter_image.get('content'):
            candidates.append(ImageCandidate(
                urljoin(page_url, twitter_image['content']),
                source='twitter:image'
            ))

        # 5. JSON-LD structured data
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                data = json.loads(script.string)
                self._extract_images_from_jsonld(data, page_url, candidates)
            except (json.JSONDecodeError, TypeError):
                pass

        # Calculate scores and filter
        for candidate in candidates:
            candidate.calculate_score()

        # Deduplicate by URL
        seen_urls = set()
        unique_candidates = []
        for candidate in candidates:
            if candidate.url not in seen_urls:
                seen_urls.add(candidate.url)
                unique_candidates.append(candidate)

        # Sort by score (highest first)
        unique_candidates.sort(key=lambda c: c.score, reverse=True)

        return unique_candidates

    def _extract_images_from_jsonld(self, data, page_url: str, candidates: List[ImageCandidate]):
        """Recursively extract image URLs from JSON-LD data."""
        if isinstance(data, dict):
            if 'image' in data:
                img = data['image']
                if isinstance(img, str):
                    candidates.append(ImageCandidate(
                        urljoin(page_url, img),
                        source='json-ld'
                    ))
                elif isinstance(img, list):
                    for i in img:
                        if isinstance(i, str):
                            candidates.append(ImageCandidate(
                                urljoin(page_url, i),
                                source='json-ld'
                            ))
                        elif isinstance(i, dict) and 'url' in i:
                            candidates.append(ImageCandidate(
                                urljoin(page_url, i['url']),
                                source='json-ld'
                            ))
                elif isinstance(img, dict) and 'url' in img:
                    candidates.append(ImageCandidate(
                        urljoin(page_url, img['url']),
                        source='json-ld'
                    ))

            for value in data.values():
                self._extract_images_from_jsonld(value, page_url, candidates)
        elif isinstance(data, list):
            for item in data:
                self._extract_images_from_jsonld(item, page_url, candidates)

    def download_image(self, url: str, index: int, referer: Optional[str] = None) -> Optional[Path]:
        """Download an image with retry logic."""
        if url in self.downloaded_urls:
            logger.debug(f"Already downloaded: {url}")
            return None

        max_retries = 3
        for attempt in range(max_retries):
            try:
                headers = {}
                if referer:
                    headers['Referer'] = referer

                response = self.session.get(url, timeout=30, headers=headers)
                response.raise_for_status()

                # Validate content type
                content_type = response.headers.get('Content-Type', '').lower()
                if not content_type.startswith('image/'):
                    logger.warning(f"Not an image (Content-Type: {content_type}): {url}")
                    return None

                # Generate filename
                url_hash = str(hash(url))[-8:]
                ext = self._get_extension_from_content_type(content_type)
                filename = f"download_{index:04d}_{url_hash}{ext}"
                filepath = self.tmp_dir / filename

                # Save to disk
                with open(filepath, 'wb') as f:
                    f.write(response.content)

                self.downloaded_urls.add(url)
                logger.info(f"Downloaded: {url} -> {filepath.name}")
                return filepath

            except requests.RequestException as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    logger.warning(f"Download failed (attempt {attempt + 1}/{max_retries}), retrying in {wait_time}s: {e}")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Download failed after {max_retries} attempts: {url} - {e}")
                    self.stats['errors'] += 1
                    return None

    def _get_extension_from_content_type(self, content_type: str) -> str:
        """Get file extension from Content-Type header."""
        mapping = {
            'image/jpeg': '.jpg',
            'image/jpg': '.jpg',
            'image/png': '.png',
            'image/webp': '.webp',
            'image/tiff': '.tiff',
            'image/bmp': '.bmp',
        }
        for ct, ext in mapping.items():
            if ct in content_type:
                return ext
        return '.jpg'  # Default

    def process_image(self, input_path: Path, output_index: int) -> Optional[Path]:
        """Process a single image for Frame TV."""
        try:
            # Load image
            with Image.open(input_path) as img:
                # Apply EXIF orientation
                img = ImageOps.exif_transpose(img)

                # Convert to RGB (handle RGBA by compositing onto black)
                if img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', img.size, (0, 0, 0))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')

                # Get current dimensions
                orig_width, orig_height = img.size
                orig_aspect = orig_width / orig_height

                # Check minimum dimensions
                if orig_width < self.args.min_width:
                    logger.info(f"Skipping {input_path.name}: width {orig_width} < minimum {self.args.min_width}")
                    self.stats['images_skipped'] += 1
                    return None

                # Check if upscaling would be needed
                if self.args.no_upscale:
                    if orig_width < self.target_width or orig_height < self.target_height:
                        logger.info(f"Skipping {input_path.name}: would require upscaling")
                        self.stats['images_skipped'] += 1
                        return None

                # Check for duplicates using perceptual hash
                if self.args.dedupe and HAS_IMAGEHASH:
                    phash = str(imagehash.phash(img))
                    if phash in self.processed_hashes:
                        logger.info(f"Skipping {input_path.name}: duplicate (perceptual hash match)")
                        self.stats['images_skipped'] += 1
                        return None
                    self.processed_hashes.add(phash)

                # Crop to target aspect ratio
                if self.args.mode == 'center':
                    img = self._center_crop_to_aspect(img, self.target_aspect)
                elif self.args.mode == 'entropy':
                    # For v1, fall back to center crop (entropy is nice-to-have)
                    img = self._center_crop_to_aspect(img, self.target_aspect)

                # Resize to target resolution
                if img.size != (self.target_width, self.target_height):
                    img = img.resize((self.target_width, self.target_height), Image.LANCZOS)

                # Generate output filename
                output_filename = f"frame_{output_index:04d}.jpg"
                output_path = self.output_dir / output_filename

                # Save with high quality
                save_kwargs = {
                    'quality': 95,
                    'optimize': True,
                    'progressive': True,
                }

                if not self.args.keep_exif:
                    save_kwargs['exif'] = b''  # Strip EXIF

                img.save(output_path, 'JPEG', **save_kwargs)

                logger.info(f"Processed: {input_path.name} -> {output_path.name} ({self.target_width}×{self.target_height})")
                self.stats['images_processed'] += 1
                return output_path

        except Exception as e:
            logger.error(f"Failed to process {input_path}: {e}")
            self.stats['errors'] += 1
            return None

    def _center_crop_to_aspect(self, img: Image.Image, target_aspect: float) -> Image.Image:
        """Center-crop image to target aspect ratio."""
        width, height = img.size
        current_aspect = width / height

        if abs(current_aspect - target_aspect) < 0.01:
            return img  # Already correct aspect ratio

        if current_aspect > target_aspect:
            # Image is wider, crop width
            new_width = int(height * target_aspect)
            left = (width - new_width) // 2
            return img.crop((left, 0, left + new_width, height))
        else:
            # Image is taller, crop height
            new_height = int(width / target_aspect)
            top = (height - new_height) // 2
            return img.crop((0, top, width, top + new_height))

    def save_manifest(self):
        """Save processing manifest to JSON."""
        manifest_path = self.output_dir / 'manifest.json'
        with open(manifest_path, 'w') as f:
            json.dump(self.manifest, f, indent=2)
        logger.info(f"Saved manifest to {manifest_path}")

    def print_summary(self):
        """Print processing summary."""
        print("\n" + "="*60)
        print("FRAMEPREP SUMMARY")
        print("="*60)
        print(f"Page Type:          {self.stats['page_type']}")
        print(f"Candidates Found:   {self.stats['candidates_found']}")
        print(f"Images Downloaded:  {self.stats['images_downloaded']}")
        print(f"Images Processed:   {self.stats['images_processed']}")
        print(f"Images Skipped:     {self.stats['images_skipped']}")
        print(f"Errors:             {self.stats['errors']}")
        print(f"Output Directory:   {self.output_dir.absolute()}")
        print("="*60)

    def run(self):
        """Main execution flow."""
        url = self.args.url

        logger.info(f"Processing URL: {url}")

        # Check if it's a direct image
        if self.is_direct_image_url(url):
            logger.info("Detected: Direct image URL")
            self.stats['page_type'] = 'direct_image'
            self.stats['candidates_found'] = 1

            # Download and process single image
            filepath = self.download_image(url, 0)
            if filepath:
                self.stats['images_downloaded'] = 1
                output_path = self.process_image(filepath, 0)
                if output_path:
                    self.manifest.append({
                        'source_url': url,
                        'downloaded_path': str(filepath),
                        'output_path': str(output_path),
                        'timestamp': time.time()
                    })
        else:
            logger.info("Detected: Webpage URL")
            self.stats['page_type'] = 'webpage'

            # Fetch and parse webpage
            try:
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                html = response.text

                # Extract candidates
                candidates = self.extract_image_candidates(html, url)
                self.stats['candidates_found'] = len(candidates)
                logger.info(f"Found {len(candidates)} image candidates")

                # Apply max limit
                if self.args.max and len(candidates) > self.args.max:
                    candidates = candidates[:self.args.max]
                    logger.info(f"Limited to {self.args.max} images")

                # Download and process each
                for i, candidate in enumerate(candidates):
                    logger.info(f"Processing candidate {i+1}/{len(candidates)}: {candidate.url[:80]}...")

                    filepath = self.download_image(candidate.url, i, referer=url)
                    if filepath:
                        self.stats['images_downloaded'] += 1
                        output_path = self.process_image(filepath, i)
                        if output_path:
                            self.manifest.append({
                                'source_url': candidate.url,
                                'original_page': url,
                                'downloaded_path': str(filepath),
                                'output_path': str(output_path),
                                'candidate_score': candidate.score,
                                'timestamp': time.time()
                            })

            except requests.RequestException as e:
                logger.error(f"Failed to fetch webpage: {e}")
                self.stats['errors'] += 1
                return 1

        # Save manifest
        if self.manifest:
            self.save_manifest()

        # Print summary
        self.print_summary()

        return 0 if self.stats['images_processed'] > 0 else 1


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='FramePrep - Prepare images from web URLs for Samsung Frame TV',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s https://example.com/image.jpg
  %(prog)s https://example.com/gallery --max 10
  %(prog)s https://example.com/page --out ./my-frames --target 1920x1080
        """
    )

    parser.add_argument('url', help='URL to process (direct image or webpage)')

    parser.add_argument('--out', default='./output',
                        help='Output directory (default: ./output)')

    parser.add_argument('--tmp', default='./tmp',
                        help='Temporary directory for downloads (default: ./tmp)')

    parser.add_argument('--target', default='3840x2160',
                        help='Target resolution WIDTHxHEIGHT (default: 3840x2160)')

    parser.add_argument('--mode', choices=['center', 'entropy'], default='center',
                        help='Cropping mode (default: center)')

    parser.add_argument('--max', type=int, default=None,
                        help='Maximum number of images to process (default: unlimited)')

    parser.add_argument('--min-width', type=int, default=1200,
                        help='Minimum width in pixels (default: 1200)')

    parser.add_argument('--no-upscale', action='store_true',
                        help='Skip images that would require upscaling')

    parser.add_argument('--dedupe', action='store_true', default=True,
                        help='Enable deduplication via perceptual hashing (default: true)')

    parser.add_argument('--no-dedupe', dest='dedupe', action='store_false',
                        help='Disable deduplication')

    parser.add_argument('--keep-exif', action='store_true',
                        help='Keep EXIF metadata in output images')

    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Enable verbose logging')

    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()

    # Configure logging level
    if args.verbose:
        logger.setLevel(logging.DEBUG)

    # Check for optional dependencies
    if args.dedupe and not HAS_IMAGEHASH:
        logger.warning("imagehash not installed, deduplication disabled")
        logger.warning("Install with: pip install imagehash")
        args.dedupe = False

    # Run FramePrep
    app = FramePrep(args)
    return app.run()


if __name__ == '__main__':
    sys.exit(main())
