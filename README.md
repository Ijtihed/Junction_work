<!-- Improved compatibility of back to top link: See: https://github.com/othneildrew/Best-README-Template/pull/73 -->
<a id="readme-top"></a>

<!-- PROJECT SHIELDS -->
[![Forks][forks-shield]][forks-url]
[![Issues][issues-shield]][issues-url]

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/Ijtihed/projectJunction">
    <h3 align="center">Junction QR Code Generator</h3>

  <p align="center">
    A QR Code Generator with authentication, customization, and history management.
    <br />
    <a href="https://github.com/Ijtihed/projectJunction"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://projectjunction.onrender.com">View Live App</a>
    ·
    <a href="https://github.com/Ijtihed/projectJunction/issues">Report Bug</a>
    ·
    <a href="https://github.com/Ijtihed/projectJunction/issues">Request Feature</a>
  </p>
</div>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#technical-details">Technical Details</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->
## About The Project

This QR Code Generator application allows users to generate, customize, and manage QR codes. The project provides:

- **Authentication**: Sign up, login, logout.
- **Customization**: Modify QR code colors, sizes, and logos.
- **History**: Save, view and delete previously generated QR codes for authenticated users.
- **Delete**: Delete some QR codes, or delete all.
- **Download**: Export QR codes as PNG files.

The app is deployed at: [Junction QR Code Generator](https://projectjunction.onrender.com).

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Built With

- Flask
- PocketBase (Database)
- HTML, CSS, JavaScript
- Python Libraries: `qrcode`, `Pillow`, etc.
- Render (Hosting)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- GETTING STARTED -->
## Getting Started

Follow these steps to set up the project locally.

### Prerequisites

- **Python 3.x**
- **pip (Python package manager)**
- **Docker Desktop**
  - **PocketBase**: A lightweight backend service used for this project. 
  - **Windows**: [Download PocketBase for Windows (amd64)](https://github.com/pocketbase/pocketbase/releases/download/v0.23.12/pocketbase_0.23.12_windows_amd64.zip)
  - **Linux**: [Download PocketBase for Linux (amd64)](https://github.com/pocketbase/pocketbase/releases/download/v0.23.12/pocketbase_0.23.12_linux_amd64.zip)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/ijtihed/projectjunction.git
   cd projectjunction
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install [Download PocketBase for Windows (amd64)](https://github.com/pocketbase/pocketbase/releases/download/v0.23.12/pocketbase_0.23.12_windows_amd64.zip) or for Linux: [Download PocketBase for Linux (amd64)](https://github.com/pocketbase/pocketbase/releases/download/v0.23.12/pocketbase_0.23.12_linux_amd64.zip) and add the .exe file to the main directory.

4. Run the application and the PocketBase Database locally:
   - Start the Flask application:
     ```bash
     python app.py
     ```
   - Start PocketBase:
     ```bash
     ./pocketbase serve
     ```

5. Initialize PocketBase schema:
   - Create a `users` collection with fields:
     - `email` (Text, Required, Unique)
     - `password` (Password, Required)
     - `role` (Text, Defaults to "user")
   - Create a `qrcodes` collection with fields:
     - `url` (Text, Required)
     - `qr_code` (Text, Required) (I recommend you increase max to 40,000)
     - `fill_color` (Text, Optional)
     - `back_color` (Text, Optional)
     - `box_size` (Number, Optional)
     - `logo_option` (Text, Optional)
     - `owner` (Relation to `users`, Required)

6. Configure environment variables:
   Create a `.env` file with:
   ```env
   SECRET_KEY=your_secret_key
   POCKETBASE_URL=http://127.0.0.1:8090
   ```

7. Visit `http://127.0.0.1:5000` in your browser.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

#### Using Docker

1. Build and start services:
   ```bash
   docker-compose up --build
   ```
2. Access services:
   - Flask app: `http://127.0.0.1:5000`
   - PocketBase: `http://127.0.0.1:8090`

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- USAGE -->
## Usage

### Required Features

- **QR Code Generation**: Enter a URL, customize the appearance, and generate a QR code.
- **Customization**:
  - Change foreground and background colors.
  - Adjust box size.
  - Embed logos.
- **History**: Save and view previously generated QR codes.
- **Download**: Export QR codes as PNG files.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- TECHNICAL DETAILS -->
# Technical Details for QR Code Generator

## Database Schema

The database uses PocketBase to manage collections. Key collections and fields include:

1. **`users` Collection (Default Collection)**:
   - Fields:
     - `id`: Unique identifier for the user.
     - `email`: User’s email address.
     - `password`: Securely hashed password.
     - `created`/`updated`: Timestamps for user management.
     - `role`: User roles. (**Not default**)

2. **`qrcodes` Collection**:
   - Fields:
     - `id`: Unique identifier for the QR code.
     - `url`: URL linked to the QR code.
     - `qr_code`: Base64-encoded QR code image.
     - `fill_color`: Foreground color of the QR code.
     - `back_color`: Background color of the QR code.
     - `box_size`: Size of the QR code grid.
     - `logo_option`: Logo type or uploaded custom logo.
     - `owner`: Reference to the user (via `users` collection).
     - `created`/`updated`: Timestamps for QR code creation and updates.
---

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## API Integration

The app integrates with PocketBase via REST API to handle data operations for both `users` and `qrcodes` collections:

<p align="right">(<a href="#readme-top">back to top</a>)</p>
---

## Frontend and Interactivity

The app includes embedded JavaScript and a dedicated `main.js` file for interactivity:


<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Color Validation

The application includes a feature to prevent users from selecting two colors that are too similar for the QR code's foreground and background. This is achieved by calculating the **color distance** between the two colors using the **Euclidean distance formula** in the RGB color space:

### Equation:

Color Distance = sqrt((R1 - R2)^2 + (G1 - G2)^2 + (B1 - B2)^2)

Where:
- \\( R_1, G_1, B_1 \\): RGB values of the first color (e.g., foreground).
- \\( R_2, G_2, B_2 \\): RGB values of the second color (e.g., background).

If the calculated color distance is below a predefined **threshold value** (e.g., 150), the application prevents the QR code generation and displays a user-friendly error message prompting the user to select more distinct colors. You can play around with this function.

This ensures a visually distinct QR code that is easier to scan.
---

## Error Handling

1. **Custom Error Pages**:
   - **404 (Not Found)**:
     ```python
     @app.errorhandler(404)
     def page_not_found(e):
         return render_template("error.html", error_title="404 - Not Found"), 404
     ```

   - **500 (Internal Server Error)**:
     ```python
     @app.errorhandler(500)
     def internal_error(e):
         return render_template("error.html", error_title="500 - Internal Error"), 500
     ```

2. **Frontend Error Messages**:
   - Alerts for invalid inputs:
     ```html
     {% if error %}
       <div class="alert alert-danger">{{ error }}</div>
     {% endif %}
     ```

---

3. **File Validation and Security**

The application includes security measures to validate uploaded files, such as logos for QR codes. Specifically:
- **Allowed File Extensions**: Only `.png`, `.jpg`, and `.jpeg` files are accepted.
- **File Name Validation**: Ensures the file name has exactly one dot and no suspicious extensions.

These features ensure the application remains secure and functional while allowing developers to set up and use PocketBase locally.

<p align="right">(<a href="#readme-top">back to top</a>)</p>
---

## QR Code Generation Workflow

1. **URL Submission**:
   - Users enter a URL, select options (color, size, logo), and submit.
   - Python:
     ```python
     if not url:
         return render_template("index.html", error="Please provide a valid URL.")
     ```

2. **QR Code Customization**:
   - Customization parameters are processed:
     ```python
     fill_color = request.form.get("fill_color", "#000000")
     back_color = request.form.get("back_color", "#ffffff")
     box_size = int(request.form.get("box_size", 10))
     ```

3. **Image Creation**:
   - Using `qrcode` and `Pillow`:
     ```python
     qr = qrcode.QRCode(box_size=box_size)
     qr.add_data(url)
     img = qr.make_image(fill_color=fill_color, back_color=back_color).convert("RGBA")
     ```

4. **Logo Embedding**:
   - Custom logos are resized and embedded:
     ```python
     logo = Image.open(logo_file).resize((img.size[0] // 4, img.size[1] // 4))
     position = ((img.size[0] - logo.size[0]) // 2, (img.size[1] - logo.size[1]) // 2)
     img.paste(logo, position, logo)
     ```

5. **Base64 Conversion**:
   - Save image as Base64 for database storage:
     ```python
     img_io = BytesIO()
     img.save(img_io, "PNG")
     qr_b64 = base64.b64encode(img_io.getvalue()).decode()
     ```
<p align="right">(<a href="#readme-top">back to top</a>)</p>
---

## Much more!

- Of course, everything can be found in the app.py python script and the main.js script and the embedded scripts in each of the HTMLs.

---
<!-- CONTACT -->
## Contact

Project Author: [Ijtihed Kilani](mailto:ijtihedk@gmail.com)

Project Link: [GitHub Repository](https://github.com/Ijtihed/projectJunction)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- MARKDOWN LINKS -->
[contributors-shield]: https://img.shields.io/github/contributors/Ijtihed/projectJunction.svg?style=for-the-badge
[contributors-url]: https://github.com/Ijtihed/projectJunction/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/Ijtihed/projectJunction.svg?style=for-the-badge
[forks-url]: https://github.com/Ijtihed/projectJunction/network/members
[stars-shield]: https://img.shields.io/github/stars/Ijtihed/projectJunction.svg?style=for-the-badge
[stars-url]: https://github.com/Ijtihed/projectJunction/stargazers
[issues-shield]: https://img.shields.io/github/issues/Ijtihed/projectJunction.svg?style=for-the-badge
[issues-url]: https://github.com/Ijtihed/projectJunction/issues
[license-shield]: https://img.shields.io/github/license/Ijtihed/projectJunction.svg?style=for-the-badge
[license-url]: https://github.com/Ijtihed/projectJunction/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/Ijtihed
