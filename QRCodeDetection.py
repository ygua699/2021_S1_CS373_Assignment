import math

from matplotlib import pyplot
from matplotlib.patches import Rectangle

import imageIO.png

class Queue:
    def __init__(self):
        self.items = []

    def isEmpty(self):
        return self.items == []

    def enqueue(self, item):
        self.items.insert(0,item)

    def dequeue(self):
        return self.items.pop()

    def size(self):
        return len(self.items)

def createInitializedGreyscalePixelArray(image_width, image_height, initValue=0):
    new_array = [[initValue for x in range(image_width)] for y in range(image_height)]
    return new_array


# this function reads an RGB color png file and returns width, height, as well as pixel arrays for r,g,b
def readRGBImageToSeparatePixelArrays(input_filename):
    image_reader = imageIO.png.Reader(filename=input_filename)
    # png reader gives us width and height, as well as RGB data in image_rows (a list of rows of RGB triplets)
    (image_width, image_height, rgb_image_rows, rgb_image_info) = image_reader.read()

    print("read image width={}, height={}".format(image_width, image_height))

    # our pixel arrays are lists of lists, where each inner list stores one row of greyscale pixels
    pixel_array_r = []
    pixel_array_g = []
    pixel_array_b = []

    for row in rgb_image_rows:
        pixel_row_r = []
        pixel_row_g = []
        pixel_row_b = []
        r = 0
        g = 0
        b = 0
        for elem in range(len(row)):
            # RGB triplets are stored consecutively in image_rows
            if elem % 3 == 0:
                r = row[elem]
            elif elem % 3 == 1:
                g = row[elem]
            else:
                b = row[elem]
                pixel_row_r.append(r)
                pixel_row_g.append(g)
                pixel_row_b.append(b)

        pixel_array_r.append(pixel_row_r)
        pixel_array_g.append(pixel_row_g)
        pixel_array_b.append(pixel_row_b)

    return (image_width, image_height, pixel_array_r, pixel_array_g, pixel_array_b)


# This method packs together three individual pixel arrays for r, g and b values into a single array that is fit for
# use in matplotlib's imshow method
def prepareRGBImageForImshowFromIndividualArrays(r, g, b, w, h):
    rgbImage = []
    for y in range(h):
        row = []
        for x in range(w):
            triple = []
            triple.append(r[y][x])
            triple.append(g[y][x])
            triple.append(b[y][x])
            row.append(triple)
        rgbImage.append(row)
    return rgbImage


# This method takes a greyscale pixel array and writes it into a png file
def writeGreyscalePixelArraytoPNG(output_filename, pixel_array, image_width, image_height):
    # now write the pixel array as a greyscale png
    file = open(output_filename, 'wb')  # binary mode is important
    writer = imageIO.png.Writer(image_width, image_height, greyscale=True)
    writer.write(file, pixel_array)
    file.close()

def computeRGBToGreyscale(pixel_array_r, pixel_array_g, pixel_array_b, image_width, image_height):
    greyscale_pixel_array = createInitializedGreyscalePixelArray(image_width, image_height)
    for i in range(image_height):
        for j in range(image_width):
            eq1 = 0.299 * pixel_array_r[i][j]
            eq2 = 0.587 * pixel_array_g[i][j]
            eq3 = 0.114 * pixel_array_b[i][j]
            greyscale_pixel_array[i][j] = round(eq1 + eq2 + eq3)
    minLst = greyscale_pixel_array[0][0]
    maxLst = greyscale_pixel_array[0][0]
    num = 0
    for i in greyscale_pixel_array:
        for j in i:
            if j > maxLst:
                maxLst = j
            if j < minLst:
                minLst = j
    if maxLst - minLst == 0:
        num = 0
    else:
        num = 255 / (maxLst - minLst)
    for i in range(image_height):
        for j in range(image_width):
            greyscale_pixel_array[i][j] = min(255, max(0, round((greyscale_pixel_array[i][j] - minLst) * num)))

    return greyscale_pixel_array


def computeVerticalEdgesSobelAbsolute(pixel_array, image_width, image_height):
    list1 = [[0 for x in range(image_width)] for y in range(image_height)]
    lst = [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]
    for i in range(1, image_height - 1):
        for j in range(1, image_width - 1):
            r1 = 0
            num1 = 0
            for x in range(i - 1, i + 2):
                num2 = 0
                for y in range(j - 1, j + 2):
                    r1 += pixel_array[x][y] * lst[num1][num2]
                    num2 += 1
                num1 += 1
            list1[i][j] = r1
    return list1


def computeHorizontalEdgesSobelAbsolute(pixel_array, image_width, image_height):
    list1 = [[0 for x in range(image_width)] for y in range(image_height)]
    lst = [[-1, -2, -1], [0, 0, 0], [1, 2, 1]]
    for i in range(1, image_height - 1):
        for j in range(1, image_width - 1):
            r1 = 0
            num1 = 0
            for x in range(i - 1, i + 2):
                num2 = 0
                for y in range(j - 1, j + 2):
                    r1 += pixel_array[x][y] * lst[num1][num2]
                    num2 += 1
                num1 += 1
            list1[i][j] = r1
    return list1


def computeMean3x3RepeatBorder(pixel_array, image_width, image_height):
    list1 = [[0 for x in range(image_width)] for y in range(image_height)]
    for i in range(1,image_height-1):
        for j in range(1,image_width-1):
            r = 0
            for x in range(i-4,i+5):
                for y in range(j-4,j+5):
                    if x >= 0 and x < image_height and y >= 0 and y < image_width:
                        r += pixel_array[x][y]

            list1[i][j] = r/81
    return list1


def computeThresholdGE(pixel_array,threshold_value, image_width, image_height):
    list1 = [[0 for x in range(image_width)] for y in range(image_height)]
    for i in range(0, image_height):
        for j in range(0, image_width):
            if pixel_array[i][j] >= threshold_value:
                list1[i][j] = 255
            else:
                list1[i][j] = 0

    return list1

def computeConnectedComponentLabeling(pixel_array, image_width, image_height):
    list1 = createInitializedGreyscalePixelArray(image_width, image_height)
    list2 = createInitializedGreyscalePixelArray(image_width, image_height)
    dict1 = {}

    label = 1
    for i in range(image_height):
        for j in range(image_width):
            if (pixel_array[i][j] > 0 and list1[i][j] != 1):
                list1[i][j] = 1
                queue = Queue()
                queue.enqueue((i, j))
                count = 0
                while not queue.isEmpty():
                    (x, y) = queue.dequeue()
                    list2[x][y] = label
                    count += 1
                    list1[x][y] = 1
                    if (x - 1 >= 0):
                        if (pixel_array[x - 1][y] > 0 and list1[x - 1][y] != 1):
                            queue.enqueue((x - 1, y))
                            list1[x - 1][y] = 1
                    if (y - 1 >= 0):
                        if (pixel_array[x][y - 1] > 0 and list1[x][y - 1] != 1):
                            queue.enqueue((x, y - 1))
                            list1[x][y - 1] = 1
                    if (y + 1 < image_width):
                        if (pixel_array[x][y + 1] > 0 and list1[x][y + 1] != 1):
                            queue.enqueue((x, y + 1))
                            list1[x][y + 1] = 1
                    if (x + 1 < image_height):
                        if (pixel_array[x + 1][y] > 0 and list1[x + 1][y] != 1):
                            queue.enqueue((x + 1, y))
                            list1[x + 1][y] = 1
                dict1[label] = count
                label += 1

    max_key = 0
    max_value = 0

    for key, value in dict1.items():
        if value > max_value:
            max_value = value
            max_key = key

    for i in range(image_height):
        for j in range(image_width):
            if list2[i][j] != max_key:
                pixel_array[i][j] = 0

    return pixel_array


def computeDilation8Nbh3x3FlatSE(pixel_array, image_width, image_height):
    lst1 = createInitializedGreyscalePixelArray(image_width, image_height)
    new_lst = [0 for i in range(image_width+2)]
    lst2 = list(pixel_array)
    for i in lst2:
        i.insert(0, 0)
        i.append(0)
    lst2 = [new_lst] + lst2 + [new_lst]
    for i in range(1, image_height+1):
        for j in range(1, image_width+1):
            x = lst2[i][j]
            x1 = lst2[i-1][j-1]
            x2 = lst2[i-1][j]
            x3 = lst2[i-1][j+1]
            x4 = lst2[i][j+1]
            x5 = lst2[i][j-1]
            x6 = lst2[i+1][j-1]
            x7 = lst2[i+1][j]
            x8 = lst2[i+1][j+1]
            if x>0 or x1>0 or x2>0 or x3>0 or x4>0 or x5>0 or x6>0 or x7>0 or x8>0:
                lst1[i-1][j-1] = 1
            else:
                lst1[i-1][j-1] = 0
    return lst1


def get_min(pixel_array, image_width, image_height):
    for i in range(image_height):
        for j in range(image_width):
            if pixel_array[i][j] > 0:
                return (j, i)


def get_max(pixel_array, image_width, image_height):
    for i in range(image_height - 1, -1, -1):
        for j in range(image_width - 1, -1, -1):
            if pixel_array[i][j] > 0:
                return (j, i)


def main():
    filename = "./images/covid19QRCode/poster1small.png"
    # filename = "./images/covid19QRCode/challenging/connecticut.png"
    threshold_value = 70
    # we read in the png file, and receive three pixel arrays for red, green and blue components, respectively
    # each pixel array contains 8 bit integer values between 0 and 255 encoding the color values
    (image_width, image_height, px_array_r, px_array_g, px_array_b) = readRGBImageToSeparatePixelArrays(filename)

    # step1: Conversion to Greyscale

    greyscale_pixel_array = computeRGBToGreyscale(px_array_r, px_array_g, px_array_b, image_width, image_height)

    # step 2: compute horizontal edges

    HorizontalEdgesSobelAbsolute = computeHorizontalEdgesSobelAbsolute(greyscale_pixel_array, image_width, image_height)

    # step 3: compute vertical edges

    VerticalEdgesSobelAbsolute = computeVerticalEdgesSobelAbsolute(greyscale_pixel_array, image_width, image_height)

    # step 4: compute edge magnitude

    for i in range(image_height):
        for j in range(image_width):
            greyscale_pixel_array[i][j] = math.sqrt(HorizontalEdgesSobelAbsolute[i][j] ** 2 + VerticalEdgesSobelAbsolute[i][j] ** 2)

    # step 5: Thresholding for Segmentation

    greyscale_pixel_array = computeMean3x3RepeatBorder(greyscale_pixel_array, image_width, image_height)

    # step 6: Morphological operations

    greyscale_pixel_array = computeThresholdGE(greyscale_pixel_array,threshold_value, image_width, image_height)

    # step 8: connected component analysis

    greyscale_pixel_array = computeConnectedComponentLabeling(greyscale_pixel_array, image_width, image_height)

    # step 9 Extract the bounding box

    list1 = computeDilation8Nbh3x3FlatSE(greyscale_pixel_array, image_width, image_height)

    x = get_min(list1, image_width, image_height)
    y = get_max(list1, image_width, image_height)
    size1 = y[1] - x[1]
    size2 = y[0] - x[0]

    pyplot.imshow(prepareRGBImageForImshowFromIndividualArrays(px_array_r, px_array_g, px_array_b, image_width, image_height))
    # pyplot.imshow(greyscale_pixel_array, cmap="gray")

    # get access to the current pyplot figure
    axes = pyplot.gca()
    # create a 70x50 rectangle that starts at location 10,30, with a line width of 3
    # rect = Rectangle((10, 30), 70, 50, linewidth=3, edgecolor='g', facecolor='none')
    # rect = Rectangle((x, y), size, size+5, linewidth=3, edgecolor='g', facecolor='none')
    rect = Rectangle((x[0],x[1]), size2 + 10, size1 + 5, linewidth=3, edgecolor='g', facecolor='none')
    # paint the rectangle over the current plot
    axes.add_patch(rect)

    # plot the current figure
    pyplot.show()


if __name__ == "__main__":
    main()
