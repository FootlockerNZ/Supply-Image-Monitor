# Supply Store Image Monitor

## Overview

This script monitors backend image loads for **Nike SKUs** on [Supply Store](https://www.supplystore.com.au), a boutique sneaker retailer known for its sluggish site performance during limited releases. By detecting when product images become available at predictable URL patterns, it can signal when a product is being staged for launch—typically within one hour of the drop. Unfortunately they have switched website providers from custom to Magento so this no longer works.

Although originally written over 5 years ago, this monitor proved highly profitable and reliable. It exploited a consistent URL structure used for product image uploads:

https://www.supplystore.com.au/images/items/{SKU}/{SKU}/1.jpg


Once an image loads successfully (HTTP 200), the script assumes the product is active in the backend and sends a Discord webhook alert, allowing users to pre-emptively log in before the frontend release.

---

## Features

- ✅ Monitors any number of Nike SKUs.
- 🔁 Multi-threaded for concurrent monitoring.
- 🧠 Detects image availability to infer backend product preparation.
- 📤 Sends rich Discord webhook notifications when a product is detected.
- 🌐 Optional proxy support for stealth and bypassing IP bans.
- 📄 Custom branding and multiple webhook targets via `backendbranding.json`.

---

## How It Works

The script performs the following operations:

1. **Load SKU List**  
   A predefined list of Nike SKUs is loaded, each containing a `SKU` code and a `title`.

2. **Initialize Proxies (Optional)**  
   If a `proxies.txt` file is present, the script loads and formats them for use in HTTP requests.

3. **Start Monitor Threads**  
   A thread is created for each SKU, enabling parallel monitoring of multiple products.

4. **Polling for Image Availability**  
   Every 3 seconds, each thread sends a GET request to: https://www.supplystore.com.au/images/items/{SKU}/{SKU}/1.jpg
   If the response returns **HTTP 200**, it suggests the image has been uploaded in the backend and the product is likely to drop soon.

5. **Webhook Notification**  
On detecting the image for the first time, the script sends a **Discord webhook embed** to all configured groups. The embed includes:
- Product title
- SKU
- Thumbnail (product image)
- Login and checkout links

6. **State Management**  
Each SKU is only notified once to avoid spamming. If the image disappears and reappears later, the alert can trigger again.

This loop continues indefinitely, making it ideal for 24/7 monitoring.

