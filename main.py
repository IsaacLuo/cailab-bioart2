import cv2
import os
import numpy as np

pens = [((230,230,230), ''), ((50,50,50), 'A1')]

def reduce_colors(img):
    height, width = img.shape[:2]
    print(width,height)
    dst_img = np.zeros((height,width,3), np.uint8)
    for i in range(height):
        for j in range(width):
            px = img[i][j]
            distance = 255*3
            chosen_pen = 0
            for pen in pens:
                color_distance = abs(px[0]-pen[0][0]) + abs(px[1]-pen[0][1]) + abs(px[2]-pen[0][2])
                if distance > color_distance:
                    distance = color_distance
                    chosen_pen = pen[0]
            dst_img[i][j] = chosen_pen
    return dst_img

def img_coord_to_pisycal_coord(x, y, w, h):
    x_range = (-56, 56)
    y_range = (-35, 35)
    xx = x*(x_range[1]-x_range[0])/w + x_range[0]
    yy = y*(y_range[1]-y_range[0])/h + y_range[0]
    return (xx, yy)


def generate_tsv(img, file_name):
    with open(file_name, 'w') as fp:
        fp.write('Source1\tMWP\t96\tSource\n')
        fp.write('Target1\tSBS\tnone\tTarget\n')
        height, width = img.shape[:2]
        for pen in pens[1:]:
            for i in range(height):
                for j in range(width):
                    if img[i][j][0] == pen[0][0] and img[i][j][1] == pen[0][1] and img[i][j][2] == pen[0][2]:
                        x, y = img_coord_to_pisycal_coord(j,i,width, height)
                        fp.write('Source1\t{0}\t{1}\tTarget1\t{2}\t{3}\n'.format(pen[1][0], pen[1][1:], y, x))

def main():
    file_names = os.listdir('pictures')
    for file_name in file_names:
        print(file_name)
        main_name, ext = os.path.splitext(file_name)
        if ext == '.png':
            img = cv2.imread(os.path.join('pictures', file_name))
            color_reduced_img = reduce_colors(img)
            cv2.imshow(main_name, color_reduced_img)
            generate_tsv(color_reduced_img, os.path.join('pixel_scripts', main_name + '.tsv'))
    cv2.waitKey()

if __name__ == "__main__":
    main()