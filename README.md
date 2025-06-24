# 🖼️ Dominant Color Extractor for Product Images

> **Note**: This is my first GitHub repository — feedback welcome!

This tool uses OpenAI to extract the **two dominant colors** from product images, which is much more efficient than doing it manually.

## 💡 Features

- 🎯 Uses **OpenAI API** to identify 2 main colors from an image.
- 💳 Requires an **OpenAI API key** (paid), but is very cost-effective compared to manual labor.
- 🆔 Requires a **unique image ID** so the extracted colors can be mapped to the correct product.
- 🖼️ Images should have a **white or transparent background**. If not, the code must be adjusted.
- 🎨 A color must occupy **at least 15% of the image** to be considered significant.

## 🚧 Limitations / Setup Notes

- Assumes clean, background-free product images.
- Code may require tweaks for colored or cluttered backgrounds.
