# FramePrep

**Web-to-Samsung-Frame Image Preparation Tool**

FramePrep is a Python tool that downloads and processes images from the web, optimizing them for display on Samsung Frame TV. It handles both direct image URLs and webpages containing multiple images, intelligently selecting the highest resolution versions available.

## Features

- 🖼️ **Smart Image Detection**: Automatically detects direct images vs. webpages
- 📐 **Perfect Frame Sizing**: Outputs images at 3840×2160 (16:9) or custom resolutions
- 🎯 **Hi-Res Selection**: Intelligently finds the highest quality images from srcset, OpenGraph tags, and more
- 🔄 **Deduplication**: Avoids processing duplicate images using perceptual hashing
- ✂️ **Smart Cropping**: Center-crop to maintain aspect ratio without distortion
- 📦 **Batch Processing**: Process entire galleries or multiple images from a single page
- 🔒 **Quality Preservation**: Uses high-quality JPEG encoding (95% quality, progressive)
- 📝 **Manifest Logging**: Tracks all processed images with source URLs and metadata

## Installation

### Requirements

- Python 3.7 or higher
- pip

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Dependencies

- `requests` - HTTP library for downloading
- `beautifulsoup4` - HTML parsing
- `pillow` - Image processing
- `lxml` - Fast HTML parser
- `imagehash` - Perceptual hashing for deduplication (optional but recommended)

## Quick Start

### Process a Direct Image URL

```bash
python frameprep.py https://example.com/beautiful-image.jpg
```

### Process a Webpage with Multiple Images

```bash
python frameprep.py https://example.com/gallery
```

### Limit to Top 5 Images

```bash
python frameprep.py https://example.com/gallery --max 5
```

### Custom Output Directory

```bash
python frameprep.py https://example.com/image.jpg --out ./my-frames
```

### Custom Resolution

```bash
python frameprep.py https://example.com/image.jpg --target 1920x1080
```

## Usage

```
usage: frameprep.py [-h] [--out OUT] [--tmp TMP] [--target TARGET]
                    [--mode {center,entropy}] [--max MAX]
                    [--min-width MIN_WIDTH] [--no-upscale] [--dedupe]
                    [--no-dedupe] [--keep-exif] [--verbose]
                    url

positional arguments:
  url                   URL to process (direct image or webpage)

optional arguments:
  -h, --help            show this help message and exit
  --out OUT             Output directory (default: ./output)
  --tmp TMP             Temporary directory for downloads (default: ./tmp)
  --target TARGET       Target resolution WIDTHxHEIGHT (default: 3840x2160)
  --mode {center,entropy}
                        Cropping mode (default: center)
  --max MAX             Maximum number of images to process
  --min-width MIN_WIDTH
                        Minimum width in pixels (default: 1200)
  --no-upscale          Skip images that would require upscaling
  --dedupe              Enable deduplication via perceptual hashing (default: true)
  --no-dedupe           Disable deduplication
  --keep-exif           Keep EXIF metadata in output images
  --verbose, -v         Enable verbose logging
```

## How It Works

### 1. URL Detection

FramePrep first determines if your URL is a direct image or a webpage:

- **Direct Image**: Downloads and processes immediately
- **Webpage**: Extracts all image candidates and selects the best ones

### 2. Image Extraction (for Webpages)

FramePrep intelligently extracts images from multiple sources:

- `<img>` tags with `src` and `srcset` attributes
- `<picture>` elements with responsive sources
- OpenGraph meta tags (`og:image`)
- Twitter Card meta tags (`twitter:image`)
- JSON-LD structured data

### 3. Hi-Res Selection

Images are scored and ranked by:

- **Dimensions**: Larger images score higher
- **Source Type**: OpenGraph and srcset images get bonuses
- **URL Analysis**: Thumbnails, icons, and sprites are penalized
- **Format**: GIF and SVG files are deprioritized

### 4. Download & Retry

- Automatic retry with exponential backoff (3 attempts)
- Referer header support for hotlink-protected images
- Content-Type validation
- Duplicate URL detection

### 5. Image Processing

Each image is processed through:

1. **EXIF Orientation Correction**: Fixes rotated images
2. **Color Mode Conversion**: Converts RGBA/palette images to RGB
3. **Aspect Ratio Cropping**: Center-crop to 16:9 (or custom ratio)
4. **Resizing**: Lanczos resampling to target resolution
5. **Quality Encoding**: 95% JPEG quality with optimization
6. **Metadata Stripping**: Removes EXIF data by default (privacy + size)

### 6. Deduplication

If enabled (default), perceptual hashing prevents processing duplicate images even if URLs differ.

## Output

FramePrep creates:

- **Processed Images**: `frame_0001.jpg`, `frame_0002.jpg`, etc. in the output directory
- **Manifest**: `manifest.json` with metadata about each processed image
- **Summary**: Console output showing what was processed

### Sample Output

```
============================================================
FRAMEPREP SUMMARY
============================================================
Page Type:          webpage
Candidates Found:   42
Images Downloaded:  10
Images Processed:   8
Images Skipped:     2
Errors:             0
Output Directory:   /home/user/output
============================================================
```

## Common Use Cases

### Art Gallery Website

```bash
python frameprep.py https://museum.org/collection/impressionism --max 20
```

### Photography Portfolio

```bash
python frameprep.py https://photographer.com/portfolio
```

### Single High-Res Image

```bash
python frameprep.py https://cdn.example.com/photo.jpg
```

### Custom Resolution for Different Frame Model

```bash
python frameprep.py https://example.com/art --target 1920x1080
```

## Troubleshooting

### 403 Forbidden Errors

Some websites block automated downloads. FramePrep includes:

- User-Agent spoofing (appears as Chrome browser)
- Referer header support (automatic for webpage images)

If still blocked, try:
- Using the direct image URL instead of the webpage
- Downloading manually and processing local files (future feature)

### Images Too Small

Adjust the minimum width threshold:

```bash
python frameprep.py https://example.com/gallery --min-width 800
```

Or allow upscaling (may reduce quality):

```bash
python frameprep.py https://example.com/gallery --min-width 800
# (upscaling is allowed by default unless --no-upscale is set)
```

### Lazy-Loaded Images Not Found

Some modern websites load images dynamically with JavaScript. Current version uses static HTML parsing.

**Workaround**: Look for direct image URLs in:
- Browser DevTools Network tab
- Page source (right-click → View Page Source)
- OpenGraph/Twitter meta tags

**Future Enhancement**: v2 will support JavaScript rendering with Playwright.

### Too Many Similar Images

Enable deduplication (default):

```bash
python frameprep.py https://example.com/gallery --dedupe
```

### Out of Disk Space

Specify a smaller batch:

```bash
python frameprep.py https://example.com/gallery --max 10
```

Clean temporary files:

```bash
rm -rf ./tmp
```

## Importing to Samsung Frame TV

### Method 1: USB Drive

1. Copy images from `./output` to a USB drive
2. Plug USB into your Frame TV
3. Go to Art Mode → Add Photos → My Collection
4. Select images from USB

### Method 2: SmartThings App

1. Open SmartThings app on your phone
2. Select your Frame TV
3. Go to Art Mode
4. Tap "Add Photos" → "My Photos"
5. Upload from phone gallery

### Method 3: Samsung Art Store (Manual)

For the authentic Frame experience, you can use FramePrep images as references to find similar art in the Samsung Art Store.

## Advanced Configuration

### Disable Deduplication

```bash
python frameprep.py https://example.com/gallery --no-dedupe
```

### Keep EXIF Metadata

```bash
python frameprep.py https://example.com/image.jpg --keep-exif
```

### Verbose Logging

```bash
python frameprep.py https://example.com/gallery --verbose
```

### Process Everything (No Limits)

```bash
python frameprep.py https://example.com/huge-gallery --min-width 0
```

## Manifest File

FramePrep creates a `manifest.json` in the output directory:

```json
[
  {
    "source_url": "https://example.com/images/photo.jpg",
    "original_page": "https://example.com/gallery",
    "downloaded_path": "tmp/download_0001_abc123.jpg",
    "output_path": "output/frame_0001.jpg",
    "candidate_score": 8294400,
    "timestamp": 1704844800.0
  }
]
```

This helps you:
- Track which images came from where
- Re-download if needed
- Audit processing results

## Supported Image Formats

### Input Formats

- JPEG (.jpg, .jpeg)
- PNG (.png)
- WebP (.webp)
- TIFF (.tif, .tiff)
- BMP (.bmp)

### Output Format

- JPEG (.jpg) - High quality (95%), optimized, progressive

## Performance Tips

1. **Use --max for large galleries**: Limit processing to avoid overwhelming storage
2. **Use --min-width to filter tiny images**: Skip thumbnails and icons
3. **Enable --no-upscale for quality**: Only process images that won't lose quality
4. **Clean tmp directory periodically**: Downloads are kept for debugging

## Known Limitations

### Current Version (v1)

- ✅ Static HTML parsing only (no JavaScript rendering)
- ✅ Center-crop only (entropy cropping planned for v2)
- ✅ No face detection (planned for v2)
- ✅ No local file input (planned for v2)

### Planned for v2

- JavaScript-rendered pages (Playwright support)
- Face-aware cropping
- Entropy-based cropping
- Local file/folder processing
- Letterbox mode (fit instead of crop)
- Bulk ZIP export

## License

MIT License - feel free to use, modify, and distribute.

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## Support

For issues, questions, or suggestions, please open an issue on GitHub.

---

**Made with ❤️ for Samsung Frame TV owners who want beautiful, perfectly-sized art.**
