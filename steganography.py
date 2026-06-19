import cv2
import numpy as np

def data2binary(data):
    """Converts text messages or pixel channel numbers into 8-bit binary strings."""
    if isinstance(data, str):
        return ''.join([format(ord(i), '08b') for i in data])
    elif isinstance(data, (bytes, np.ndarray)):
        return [format(i, '08b') for i in data]
    elif isinstance(data, (int, np.uint8)):
        return format(data, '08b')

def hidedata(img, data):
    """Embeds the binary text data into the LSBs of the RGB channels."""
    data += "$$"  # '$$' acts as the stop marker for decoding
    d_index = 0
    b_data = data2binary(data)
    len_data = len(b_data)

    # Go through every row and column of pixels in the RGB image
    for row in img:
        for pix in row:
            # Convert current Red, Green, and Blue values into binary strings
            r, g, b = data2binary(pix[0]), data2binary(pix[1]), data2binary(pix[2])
            
            # Hide a bit in the Red channel's LSB
            if d_index < len_data:
                pix[0] = int(r[:-1] + b_data[d_index], 2)
                d_index += 1
            # Hide a bit in the Green channel's LSB
            if d_index < len_data:
                pix[1] = int(g[:-1] + b_data[d_index], 2)
                d_index += 1
            # Hide a bit in the Blue channel's LSB
            if d_index < len_data:
                pix[2] = int(b[:-1] + b_data[d_index], 2)
                d_index += 1
                
            # If the entire message is hidden, stop processing pixels
            if d_index >= len_data:
                break
        if d_index >= len_data:
            break
    return img

def encode():
    img_name = input("Enter source color image name (e.g., cover.png): ")
    image = cv2.imread(img_name)
    if image is None:
        print("Error: Could not open image file.")
        return

    data = input("Enter the secret text message to hide: ")
    if len(data) == 0:
        print("Error: Message cannot be empty.")
        return
        
    enc_img = input("Enter output image name (Must end in .png to avoid data loss): ")
    if not enc_img.lower().endswith('.png'):
        print("Warning: Adding '.png' extension to protect data integrity.")
        enc_img += ".png"

    # Hide data and write out as a lossless file
    enc_data = hidedata(image, data)
    cv2.imwrite(enc_img, enc_data)
    print(f"🎉 Success! Secret message successfully hidden inside {enc_img}")

def find_data(img):
    """Extracts hidden text from the LSBs of an image until '$$' is reached."""
    bin_data = ""
    for row in img:
        for pix in row:
            r, g, b = data2binary(pix[0]), data2binary(pix[1]), data2binary(pix[2])
            bin_data += r[-1]  # Extract Red LSB
            bin_data += g[-1]  # Extract Green LSB
            bin_data += b[-1]  # Extract Blue LSB

    # Group collected bits into 8-bit bytes
    all_bytes = [bin_data[i: i + 8] for i in range(0, len(bin_data), 8)]

    readable_data = ""
    for x in all_bytes:
        readable_data += chr(int(x, 2))
        # Cut off processing the moment our stop marker is found
        if readable_data[-2:] == "$$":
            break
            
    return readable_data[:-2]

def decode():
    img_name = input("Enter the path of the steganographed PNG image: ")
    image = cv2.imread(img_name)
    if image is None:
        print("Error: Could not open image file.")
        return ""
    
    msg = find_data(image)
    return msg

def steganography():
    while True:
        print("\n=== Image Steganography (RGB) ===")
        print("1. Encode (Hide Text)")
        print("2. Decode (Extract Text)")
        print("3. Exit")
        
        try:
            u_in = int(input("\nEnter your choice (1-3): "))
            if u_in == 1:
                encode()
            elif u_in == 2:
                ans = decode()
                print("\n🔓 Extracted Message: " + ans)
            elif u_in == 3:
                print("Exiting tool. Goodbye!")
                break
            else:
                print("Invalid choice. Please enter 1, 2, or 3.")
        except ValueError:
            print("Please enter a valid numeric choice.")

if __name__ == "__main__":
    steganography()
