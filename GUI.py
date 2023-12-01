from importlib.resources import path
from tkinter import *
from tkinter import filedialog, ttk, messagebox
from PIL import ImageTk, Image, ExifTags, ImageChops
from optparse import OptionParser
from datetime import datetime
from matplotlib import image
from prettytable import PrettyTable
import numpy as np
import random
import sys
import cv2
import re
import os
from pyparsing import Opt
from ForgeryDetection import Detect
import copy_move_cfa


# Global variables
IMG_WIDTH = 400
IMG_HEIGHT = 400
uploaded_image = None

# copy-move parameters
cmd = OptionParser("usage: %prog image_file [options]")
# if not args:
#     cmd.print_help()
#     sys.exit()


def getImage(path, width, height):
    img = Image.open(path)
    img = img.resize((width, height), Image.LANCZOS)
    return ImageTk.PhotoImage(img)

def browseFile():

    filename = filedialog.askopenfilename(title="Select an image", filetypes=[("image", ".jpeg"),("image", ".png"),("image", ".jpg")])
    if filename == "":
        return

    global uploaded_image
    uploaded_image = filename
    progressBar['value'] = 0
    fileLabel.configure(text=filename)

    img = getImage(filename, IMG_WIDTH, IMG_HEIGHT)
    imagePanel.configure(image=img)
    imagePanel.image = img

    blank_img = getImage("images/output.png", IMG_WIDTH, IMG_HEIGHT)
    resultPanel.configure(image=blank_img)
    resultPanel.image = blank_img

    resultLabel.configure(text="READY TO SCAN", foreground="green")


def copy_move_forgery():
    # Retrieve path
    path = uploaded_image
    eps = 60
    min_samples = 2

    if path is None:
        messagebox.showerror('Error', "Please select image")
        return

    detect = Detect(path)
    key_points, descriptors = detect.siftDetector()
    forgery = detect.locateForgery(eps, min_samples)

    # Set the progress bar to 100%
    progressBar['value'] = 100

    if forgery is None:
        # Retrieve the thumbs up image and display in resultPanel
        img = getImage("images/no_copy_move.png", IMG_WIDTH, IMG_HEIGHT)
        resultPanel.configure(image=img)
        resultPanel.image = img

        # Display results in resultLabel
        resultLabel.configure(text="ORIGINAL IMAGE", foreground="green")
    else:
        # Retrieve the output image and display in resultPanel
        img = getImage("images/copy_move.png", IMG_WIDTH, IMG_HEIGHT)
        resultPanel.configure(image=img)
        resultPanel.image = img

        # Display results in resultLabel
        resultLabel.configure(text="Image Forged", foreground="red")
        # cv2.imshow('Original image', detect.image)
        cv2.imshow('Forgery', forgery)
        wait_time = 1000
        while(cv2.getWindowProperty('Forgery', 0) >= 0) or (cv2.getWindowProperty('Original image', 0) >= 0):
            keyCode = cv2.waitKey(wait_time)
            if (keyCode) == ord('q') or keyCode == ord('Q'):
                cv2.destroyAllWindows()
                break
            elif keyCode == ord('s') or keyCode == ord('S'):
                name = re.findall(r'(.+?)(\.[^.]*$|$)', path)
                date = datetime.today().strftime('%Y_%m_%d_%H_%M_%S')
                new_file_name = name[0][0]+'_'+str(eps)+'_'+str(min_samples)
                new_file_name = new_file_name+'_'+date+name[0][1]

                vaue = cv2.imwrite(new_file_name, forgery)
                print('Image Saved as....', new_file_name)


def metadata_analysis():
    # Retrieve the path of the image file
    path = uploaded_image
    # User has not selected an input image
    if path is None:
        # Show error message
        messagebox.showerror('Error', "Please select image")
        return

    img = Image.open(path)
    img_exif = img.getexif()

    # Set the progress bar to 100%
    progressBar['value'] = 100

    if img_exif is None:
        # print('Sorry, image has no exif data.')
        # Retrieve the output image and display in resultPanel
        img = getImage("images/no_metadata.png", IMG_WIDTH, IMG_HEIGHT)
        resultPanel.configure(image=img)
        resultPanel.image = img

        # Display results in resultLabel
        resultLabel.configure(text="NO Data Found", foreground="red")
    else:
        # Retrieve the thumbs up image and display in resultPanel
        img = getImage("images/metadata.png", IMG_WIDTH, IMG_HEIGHT)
        resultPanel.configure(image=img)
        resultPanel.image = img

        # Display results in resultLabel
        resultLabel.configure(text="Metadata Details", foreground="green")

        # print('image has exif data.')
        with open('Metadata_analysis.txt', 'w') as f:
            for key, val in img_exif.items():
                if key in ExifTags.TAGS:
                    # print(f'{ExifTags.TAGS[key]} : {val}')
                        f.write(f'{ExifTags.TAGS[key]} : {val}\n')
        os.startfile('Metadata_analysis.txt')

def cfa_artifact():
    # Retrieve the path of the image file
    path = uploaded_image
    # User has not selected an input image
    if path is None:
        # Show error message
        messagebox.showerror('Error', "Please select image")
        return

    identical_regions_cfa = copy_move_cfa.detect(path, opt, args)
    # identical_regions_cfa = copy_move_cfa.detect(path, opt, args)


    # Set the progress bar to 100%
    progressBar['value'] = 100

    # print('\n' + str(identical_regions_cfa), 'CFA artifacts detected')

    if(identical_regions_cfa):
        # Retrieve the output image and display in resultPanel
        img = getImage("images/cfa.png", IMG_WIDTH, IMG_HEIGHT)
        resultPanel.configure(image=img)
        resultPanel.image = img

        # Display results in resultLabel
        resultLabel.configure(text=f"{str(identical_regions_cfa)}, CFA artifacts detected", foreground="red")

    else:
        # print('\nSingle compressed')
        # Retrieve the thumbs up image and display in resultPanel
        img = getImage("images/no_cfa.png", IMG_WIDTH, IMG_HEIGHT)
        resultPanel.configure(image=img)
        resultPanel.image = img

        # Display results in resultLabel
        resultLabel.configure(text="NO-CFA artifacts detected", foreground="green")


def ela_analysis():
    # Retrieve the path of the image file
    path = uploaded_image
    TEMP = 'temp.jpg'
    SCALE = 10

    # User has not selected an input image
    if path is None:
        # Show error message
        messagebox.showerror('Error', "Please select image")
        return

    original = Image.open(path)
    original.save(TEMP, quality=90)
    temporary = Image.open(TEMP)

    diff = ImageChops.difference(original, temporary)
    d = diff.load()
    WIDTH, HEIGHT = diff.size
    for x in range(WIDTH):
        for y in range(HEIGHT):
            d[x, y] = tuple(k * SCALE for k in d[x, y])

    # Set the progress bar to 100%
    progressBar['value'] = 100
    diff.show()



def jpeg_Compression():

    # Retrieve the path of the image file
    path = uploaded_image
    # User has not selected an input image
    if path is None:
        # Show error message
        messagebox.showerror('Error', "Please select image")
        return

    double_compressed = double_jpeg_compression.detect(path)

    # Set the progress bar to 100%
    progressBar['value'] = 100

    if(double_compressed):
        # print('\nDouble compression detected')
        # Retrieve the output image and display in resultPanel
        img = getImage("images/double_compression.png", IMG_WIDTH, IMG_HEIGHT)
        resultPanel.configure(image=img)
        resultPanel.image = img

        # Display results in resultLabel
        resultLabel.configure(text="Double compression", foreground="red")

    else:
        # print('\nSingle compressed')
        # Retrieve the thumbs up image and display in resultPanel
        img = getImage("images/single_compression.png", IMG_WIDTH, IMG_HEIGHT)
        resultPanel.configure(image=img)
        resultPanel.image = img

        # Display results in resultLabel
        resultLabel.configure(text="Single compression", foreground="green")

def image_decode():
    # Retrieve the path of the image file
    path = uploaded_image
    # User has not selected an input image
    if path is None:
        # Show error message
        messagebox.showerror('Error', "Please select image")
        return

    # Encrypted image
    img = cv2.imread(path)
    width = img.shape[0]
    height = img.shape[1]

    # img1 and img2 are two blank images
    img1 = np.zeros((width, height, 3), np.uint8)
    img2 = np.zeros((width, height, 3), np.uint8)

    for i in range(width):
        for j in range(height):
            for l in range(3):
                v1 = format(img[i][j][l], '08b')
                v2 = v1[:4] + chr(random.randint(0, 1)+48) * 4
                v3 = v1[4:] + chr(random.randint(0, 1)+48) * 4

                img1[i][j][l]= int(v2, 2)
                img2[i][j][l]= int(v3, 2)

    # Set the progress bar to 100%
    progressBar['value'] = 100

    cv2.imwrite('output.png', img2)

    im = Image.open('output.png')
    im.show()

def string_analysis():
    # Retrieve the path of the image file
    path = uploaded_image
    # User has not selected an input image
    if path is None:
        # Show error message
        messagebox.showerror('Error', "Please select image")
        return

    x=PrettyTable()
    x.field_names = ["Bytes", "8-bit", "string"]
    with open(path, "rb") as f:
            n = 0
            b = f.read(16)

            while b:
                s1 = " ".join([f"{i:02x}" for i in b])
                s1 = s1[0:23] + " " + s1[23:]

                # ascii string; chained comparison
                s2 = "".join([chr(i) if 32 <= i <= 127 else "." for i in b])
                x.add_row([f"{n * 16:08x}",f"{s1:<48}",f"{s2}"])

                n += 1
                b = f.read(16)

            # Set the progress bar to 100%
            progressBar['value'] = 100

            with open('hex_viewer.txt', 'w') as w:
                w.write(str(x))
            os.startfile('hex_viewer.txt')

# Initialize the app window
root = Tk()
root.title("Copy-Move Detector")
root.iconbitmap('images/favicon.ico')

# Ensure the program closes when window is closed
root.protocol("WM_DELETE_WINDOW", root.quit)

# Maximize the size of the window
root.state("zoomed")

# Add the GUI into the Tkinter window
# GUI(parent=root)

# Label for the results of scan
resultLabel = Label(text="IMAGE FORGERY DETECTOR", font=("Courier", 50))
resultLabel.grid(row=0, column=0, columnspan=3)


# Get the blank image
input_img = getImage("images/input.png", IMG_WIDTH, IMG_HEIGHT)
middle_img = getImage("images/middle.png", IMG_WIDTH, IMG_HEIGHT)
output_img = getImage("images/output.png", IMG_WIDTH, IMG_HEIGHT)


# Displays the input image
imagePanel = Label(image=input_img)
imagePanel.image = input_img
imagePanel.grid(row=1, column=0, padx=5)


# Label to display the middle image
middle = Label(image=middle_img)
middle.image = middle_img
middle.grid(row=1, column=1, padx=5)


# Label to display the output image
resultPanel = Label(image=output_img)
resultPanel.image = output_img
resultPanel.grid(row=1, column=2, padx=5)


# Label to display the path of the input image
fileLabel = Label(text="No file selected", fg="grey", font=("Times", 15))
fileLabel.grid(row=2, column=1)


# Progress bar
progressBar = ttk.Progressbar(length=500)
progressBar.grid(row=3, column=1)


# Configure the style of the buttons
s = ttk.Style()
s.configure('my.TButton', font=('Times', 15))


# Button to upload images
uploadButton = ttk.Button(
    text="Upload Image", style="my.TButton", command=browseFile)
uploadButton.grid(row=4, column=1, sticky="nsew", pady=5)


# Button to run the Metadata-Analysis detection algorithm
metadata = ttk.Button(text="Metadata-Analysis",
                      style="my.TButton", command=metadata_analysis)
metadata.grid(row=5, column=0, columnspan=2, pady=20)


# Button to run the CFA-artifact detection algorithm
artifact = ttk.Button(text="CFA-artifact detection", style="my.TButton", command=cfa_artifact)
artifact.grid(row=5, column=1, columnspan=1, pady=20)


# Button to run the Copy-Move  detection algorithm
copy_move = ttk.Button(text="Copy-Move", style="my.TButton", command=copy_move_forgery)
copy_move.grid(row=5, column=2, columnspan=1, pady=20)


# Button to exit the program
style = ttk.Style()
style.configure('W.TButton', font = ('calibri', 10, 'bold'),foreground = 'red')
quitButton = ttk.Button(text="Exit program", style = 'W.TButton', command=root.quit)
quitButton.grid(row=6, column=2, pady=5)



root.mainloop()
