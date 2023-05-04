import os
import sys
import time

from argparse import ArgumentParser
from pathlib import Path

import blend_modes
import cv2
import numpy

parser = ArgumentParser()
parser.add_argument("-c", "--camera-id", type=int, help="Camera ID (default: 0)", default=0)
parser.add_argument("--opacity", type=float, help="Opacity to blend images (default: 0.3125)", default=0.3125)
parser.add_argument("--save", action="store_true", help="Save captured frames to images/ folder", default=False)
parser.add_argument("-s", "--seconds", type=int, help="Seconds to capturing images (default: 10)", default=10)
parser.add_argument("--size", help="Image size (default: 640x480)", default="640x480", type=str)
parser.add_argument("--input-dir", action="store_true", help="Input directory instead of camera", default=False)
parser.add_argument("-o", "--output", help="Output file name (default: output.png)", default="output.png", type=str)
# parser.add_argument("-f", "--fps", type=int, help="FPS (default: auto)", default=None)
args = parser.parse_args()

def frame() -> numpy.ndarray:
    _, frame = cam.read()
    return frame

def capture_images() -> numpy.ndarray:
    sys.stdout.write("Initializing camera...\r")
    init = [frame() for _ in range(50)]
    if not init[1].any():
        print("Unable to initialize camera.")
        sys.exit()
    del init
    
    image = frame()
    sizeX, sizeY, channels = image.shape
    
    max_fps = cam.get(cv2.CAP_PROP_FPS)
    # sleep_time = 0
    # if args.fps is not None:
    #     if args.fps > max_fps:
    #         print(f"Warning: ({args.fps}FPS) is higher than camera's max FPS. Setting to {max_fps}FPS.")
    #     else:
    #         cam.set(cv2.CAP_PROP_FPS, args.fps)
    #     if not args.fps == max_fps:
    #         sleep_time = 1 / args.fps
    
    if not args.seconds > 0:
        print("Warning: Seconds must be higher than 0. Setting to 10.")
        args.seconds = 10
    
    MAX_PHOTO_COUNT: int = round(args.seconds * max_fps)
    
    captured_frames = numpy.empty((MAX_PHOTO_COUNT, sizeX, sizeY, channels), dtype=numpy.uint8)
    
    seconds = args.seconds
    hours = seconds // 3600
    remaining_seconds = seconds % 3600
    minutes = remaining_seconds // 60
    remaining_seconds %= 60
    
    if hours > 0:
        timemeta = f"{hours}h {minutes}m {remaining_seconds}s"
    elif minutes > 0:
        timemeta = f"{minutes}m {remaining_seconds}s"
    else:
        timemeta = f"{remaining_seconds}s"
    
    channel = "RGB" if channels == 3 else "RGBA"
    
    print("-"*24)
    print(f"Camera ID: {args.camera_id}")
    print(f"FPS: {max_fps}, {timemeta}")
    print(f"Max photo count: {MAX_PHOTO_COUNT}")
    print(f"Image size: {sizeX}x{sizeY}")
    print(f"Channels: {channel}({channels})")
    print("-"*24)
    
    time.sleep(0.15)
    
    start_time = time.perf_counter()
    for i in range(1, MAX_PHOTO_COUNT):
        image = frame()
        
        sys.stdout.write(f"Capturing frame: {i+1}.   \r")
        sys.stdout.flush()
        
        captured_frames[i] = image
    
    n = round(time.perf_counter() - start_time, 2)
    sys.stdout.write(f"Captured {MAX_PHOTO_COUNT} frames.      \n")
    sys.stdout.write(f"Took {n} seconds.\n")
    return captured_frames

def read_images_from_dir() -> numpy.ndarray:
    directories = os.listdir("images/")
    directories.sort()
    
    if len(directories) == 0:
        print("No images folder found in images/ folder.")
        sys.exit()
    
    print("Which folder do you want to use?")
    for i, d in enumerate(directories):
        print(f"{i+1}. {d}")
        
    while True:
        try:
            choice = int(input("Choice: "))
            if choice > len(directories) or choice < 1:
                raise ValueError
            break
        except ValueError:
            print("Invalid choice.")
    
    from pathlib import Path
    images = [i for i in Path(f"images/{directories[choice-1]}").iterdir() if i.is_file()]
    images.sort()
    
    img0 = cv2.imread(str(images[0]))
    sizeX, sizeY, channels = img0.shape
    
    captured_frames = numpy.empty((len(images), sizeX, sizeY, channels), dtype=numpy.uint8)
    for i, img in enumerate(images):
        sys.stdout.write(f"Importing frame{i+1}   \r")
        sys.stdout.flush()
        captured_frames[i] = cv2.imread(str(img))
    
    return captured_frames
     

def process_images(images: numpy.ndarray) -> numpy.ndarray:
    img0 = cv2.cvtColor(images[0], cv2.COLOR_BGR2BGRA)
    img0f = img0.astype(float)
    sys.stdout.write(f"Processing image 1   \r")
    
    for index, i in enumerate(images[1:][::-1]):
        img1 = cv2.cvtColor(i, cv2.COLOR_BGR2BGRA)
        sys.stdout.flush()
        sys.stdout.write(f"Processing image {index+2}  \r")
        img1f = img1.astype(float)
        img0f = blend_modes.lighten_only(img0f, img1f, opacity=args.opacity)
        blend = img0f.astype(numpy.uint8)
        cv2.imshow('image', blend)
        cv2.waitKey(6)
    return blend

def main():
    try:
        if args.input_dir:
            images = read_images_from_dir()
        else:
            images = capture_images()
        
        start = time.perf_counter()
        
        image = process_images(images)
        n = round(time.perf_counter() - start, 2)
        print(f"\nRender took {n} seconds.")
        cv2.imwrite(args.output, image)
        print(f"Saved to {args.output}.")
    except KeyboardInterrupt:
        cam.release()
        cv2.destroyAllWindows()
        sys.exit()
        
    if args.save and not args.input_dir:
        img_path = Path("images")
        img_path.mkdir(exist_ok=True)
        
        folder_name = f"{time.strftime('%Y-%m-%d-%H-%M-%S')}-cam{args.camera_id}-images"
        folder_path = img_path / folder_name
        folder_path.mkdir(exist_ok=True)
        
        print("Saving images...")
        for i, image in enumerate(images):
            cv2.imwrite(str(folder_path / f"{i}.png"), image)
    
    sys.stdout.write("\nDone! Press 'q' to exit.")
    
    try:
        cv2.waitKey(0) & 0xFF == ord('q')
    except KeyboardInterrupt:
        pass
    
    cam.release()
    cv2.destroyAllWindows()
    sys.exit()

if __name__ == "__main__":    
    cam = cv2.VideoCapture(int(args.camera_id))
    
    w,h = map(int, args.size.split("x"))
    
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, w)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
    cam.set(cv2.CAP_PROP_ISO_SPEED, 50)
    
    main()
