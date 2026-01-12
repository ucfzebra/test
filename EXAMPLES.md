# FramePrep Usage Examples

This document provides real-world usage examples for FramePrep.

## Basic Examples

### Example 1: Process a Single Image

```bash
python frameprep.py https://images.unsplash.com/photo-1506905925346-21bda4d32df4
```

**What happens:**
- Downloads the image
- Crops to 16:9 if needed
- Resizes to 3840×2160
- Saves as `output/frame_0001.jpg`

---

### Example 2: Gallery with Limit

```bash
python frameprep.py https://example.com/nature-gallery --max 10
```

**What happens:**
- Extracts all image candidates from the page
- Ranks them by resolution and quality
- Downloads top 10 images
- Processes each one
- Outputs `frame_0001.jpg` through `frame_0010.jpg`

---

### Example 3: Custom Resolution for Frame TV Lifestyle

```bash
python frameprep.py https://example.com/art.jpg --target 1920x1080 --out ./lifestyle
```

**What happens:**
- Processes to 1920×1080 instead of 3840×2160
- Saves to `./lifestyle` directory
- Perfect for Frame TV Lifestyle mode

---

### Example 4: High-Quality Photography (No Upscaling)

```bash
python frameprep.py https://photographer.com/portfolio --no-upscale --min-width 2000
```

**What happens:**
- Only processes images ≥2000px wide
- Skips any image that would need upscaling
- Ensures maximum quality preservation

---

### Example 5: Process Everything (Archive Mode)

```bash
python frameprep.py https://archive.org/details/art-collection --min-width 0 --no-dedupe
```

**What happens:**
- No minimum width filter (processes all sizes)
- No deduplication (keeps all variations)
- Useful for archiving complete collections

---

## Advanced Examples

### Example 6: Batch Processing Multiple URLs

Create a script `batch_process.sh`:

```bash
#!/bin/bash

urls=(
    "https://site1.com/gallery1"
    "https://site2.com/gallery2"
    "https://site3.com/gallery3"
)

for i in "${!urls[@]}"; do
    python frameprep.py "${urls[$i]}" --out "./output/batch_$i" --max 20
done
```

Run with:
```bash
chmod +x batch_process.sh
./batch_process.sh
```

---

### Example 7: Keep Original Metadata

```bash
python frameprep.py https://photographer.com/photo.jpg --keep-exif
```

**Use case:** When you want to preserve:
- Copyright information
- Camera settings
- GPS data
- Date taken

---

### Example 8: Debugging Failed Downloads

```bash
python frameprep.py https://problematic-site.com/gallery --verbose
```

**What happens:**
- Shows detailed logging
- Displays download attempts
- Reveals why images are skipped
- Helpful for troubleshooting 403 errors

---

## Site-Specific Examples

### Unsplash

```bash
python frameprep.py "https://unsplash.com/collections/your-collection" --max 50
```

### Wikimedia Commons

```bash
python frameprep.py "https://commons.wikimedia.org/wiki/File:Example.jpg"
```

### Your Own Website

```bash
python frameprep.py "https://yourdomain.com/portfolio" --max 25 --min-width 1920
```

---

## Testing Examples

### Test with Different Resolutions

```bash
# 4K Ultra HD (Frame TV default)
python frameprep.py URL --target 3840x2160

# Full HD
python frameprep.py URL --target 1920x1080

# Custom aspect ratio (e.g., 21:9 ultrawide)
python frameprep.py URL --target 2560x1080
```

### Test Cropping Behavior

```bash
# Portrait image → cropped to landscape
python frameprep.py https://example.com/portrait.jpg

# Square image → cropped to 16:9
python frameprep.py https://example.com/square.jpg

# Already 16:9 → minimal processing
python frameprep.py https://example.com/landscape.jpg
```

---

## Production Workflow

### Complete Frame TV Setup

```bash
# Step 1: Download and process art
python frameprep.py https://museum.org/impressionism --max 30 --out ./art-collection

# Step 2: Review manifest
cat ./art-collection/manifest.json | jq .

# Step 3: Copy to USB
cp ./art-collection/*.jpg /media/usb/FrameArt/

# Step 4: Safely eject USB
umount /media/usb
```

---

## Troubleshooting Examples

### Handle 403 Forbidden

If you get 403 errors, try using the browser's developer tools to find direct image URLs:

1. Open page in browser
2. Right-click image → "Copy image address"
3. Use that direct URL:

```bash
python frameprep.py "https://cdn.example.com/direct-image-url.jpg"
```

### Check What Would Be Downloaded (Dry Run)

Currently not supported, but you can check with verbose mode and `--max 1`:

```bash
python frameprep.py URL --max 1 --verbose
```

---

## Performance Examples

### Fast Mode (Top 5 Only)

```bash
python frameprep.py URL --max 5 --min-width 1920
```

### Maximum Quality Mode

```bash
python frameprep.py URL --no-upscale --min-width 3840 --keep-exif
```

### Balanced Mode (Recommended)

```bash
python frameprep.py URL --max 20 --min-width 1200 --dedupe
```

---

## Output Organization

### Organize by Theme

```bash
python frameprep.py https://nature.com/landscapes --out ./frames/nature
python frameprep.py https://art.com/abstract --out ./frames/abstract
python frameprep.py https://photos.com/cityscapes --out ./frames/cities
```

### Result:
```
frames/
├── nature/
│   ├── frame_0001.jpg
│   ├── frame_0002.jpg
│   └── manifest.json
├── abstract/
│   ├── frame_0001.jpg
│   └── manifest.json
└── cities/
    ├── frame_0001.jpg
    └── manifest.json
```

---

## Tips & Tricks

1. **Always check the manifest** - Review `manifest.json` to see source URLs
2. **Start small** - Use `--max 5` first to test before full processing
3. **Use --verbose** - When things don't work as expected
4. **Clean tmp regularly** - Downloads accumulate in `./tmp`
5. **Check resolution** - Open output images to verify quality

---

## Common Error Solutions

### "No images found"
- Page might be JavaScript-rendered (try finding direct URLs)
- Check with `--verbose` to see what was detected

### "All images too small"
- Lower `--min-width` threshold
- Check if site serves hi-res versions (look for srcset)

### "Out of disk space"
- Use `--max` to limit quantity
- Clean `./tmp` directory

### "Download failed"
- Site might block automated access
- Try copying direct image URL from browser

---

**Pro Tip:** Combine FramePrep with frame rotation scripts to automatically cycle through your art collection on Samsung Frame TV!
