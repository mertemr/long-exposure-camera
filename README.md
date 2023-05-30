# Long Exposure Camera
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Long Exposure Camera is a Python program that blends captured frames from a camera or imported from a directory of images.

## Dependencies
To run the code, you need to install the following dependencies:

- OpenCV (`cv2`)
- Numpy
- Blend Modes

You can install with the following command:
```bash
pip install -r requirements.txt
```
You also need to have **Python 3.6 or above** installed.

## Usage
python *app* `[-h] [-c CAMERA_ID] [--opacity OPACITY] [--save] [-s SECONDS] [--size SIZE] [--input-dir] [-o OUTPUT]`

Here are the descriptions of the arguments:
```md
- `-h`, `--help`: Shows the help message and exits.
- `-c CAMERA_ID`, `--camera-id CAMERA_ID`: Specifies the camera ID (default: 0).
- `--opacity OPACITY`: Specifies the opacity to blend images (default: 0.3125).
- `--save`: Saves the captured frames to the "images/" folder.
- `-s SECONDS`, `--seconds SECONDS`: Specifies the duration of capturing frames in seconds (default: 10).
- `--size SIZE`: Specifies the image size (default: 640x480).
- `--input-dir`: Uses an input directory instead of a camera.
- `-o OUTPUT`, `--output OUTPUT`: Specifies the output file name (default: output.png).
```

## Examples
To process frames by capturing from camera:
```bash
python app
```

To process frames by importing them from a directory of images:
```bash
python app --input-dir
```

To blend the frames and save the output as "output.png":
```bash
python app --save -o output.png
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
