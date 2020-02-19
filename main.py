import cv2
import os
import numpy as np
import random

pens = [((0,15,33), 'A'), ((0,153,255), 'B'), ((230,230,230), 'C')]
pen_count = [0,0,0]
g_width=192
g_height=128

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

def colnum_string(n):
    string = ""
    while n > 0:
        n, remainder = divmod(n-1, 26)
        string = chr(65 + remainder) + string
    return string

def generate_csv(img, file_name):
    with open(file_name, 'w') as fp:
        fp.write('Source Plate Name,Source Plate Type,Source Well,Destination Plate Name,Destination Well,Transfer Volume,Destination Well X Offset,Destination Well Y Offset,Delay\n')
        height, width = img.shape[:2]
        for k,pen in enumerate(pens):
            for i in range(height):
                for j in range(width):
                    if img[i][j][0] == pen[0][0] and img[i][j][1] == pen[0][1] and img[i][j][2] == pen[0][2]:
                        dst_well_name = '{}{}'.format(colnum_string(i+1), j+1)
                        fp.write('Plate1,384PP_AQ_BP,{}{},Plate2,{},10,0,0,0\n'.format(pen[1],(pen_count[k]//5000)+1,dst_well_name))
                        pen_count[k]+=1
    

# convert one reduced color Image to multiple binary images
def split_color(img):
    ret = []
    pens = {}
    height, width = img.shape[:2]
    for i in range(height):
        for j in range(width):
            pxl = img[i][j]
            p = (pxl[0], pxl[1], pxl[2], )
            if p not in pens:
                picture = np.zeros((height,width,1), np.uint8)
                pens[p] = picture
                ret.append(picture)
            else:
                picture = pens[p]
            # for i, p2 in enumerate(pens):
            #     if np.array_equal(pxl, p2):
            #         picture = ret[i]
            #         break
            # else:
            #     pens.append(pxl)
            #     picture = np.zeros((height,width,1), np.uint8)
            #     ret.append(picture)
            picture[i][j] = 255
    return ret

def show_large(name, img):
    height, width = img.shape[:2]
    cv2.imshow(
        name, 
        cv2.resize(img, (width*5, height*5), interpolation=cv2.INTER_NEAREST)
    )


def gen_commands_by_boundry_order(img, src_well, channel_id):
    cmd_list = []
    for i in range(9):
        cmd_list.append([])

    height, width = img.shape[:2]
    for i in range(height):
        for j in range(width):
            if img[i][j] == 255:
                same_color_count = -1
                for dx in range(-1, 2):
                    for dy in range(-1, 2):
                        if i+dy >= 0 and i+dy < height and j+dx>=0 and j+dx < width and img[i+dy][j+dx]==255:
                            same_color_count+=1
                cmd_list[same_color_count].append({"x":j, "y":i, "bi":same_color_count, 'src': src_well, 'channel_id':channel_id})
    return cmd_list

def main():
    file_names = os.listdir('pictures')
    for file_name in file_names:
        print(file_name)
        main_name, ext = os.path.splitext(file_name)
        if ext == '.png':
            img = cv2.imread(os.path.join('pictures', file_name))
            color_reduced_img = reduce_colors(img)
            channels = split_color(color_reduced_img)
            # for i, c in enumerate(channels):
            #     show_large('%d'%i, c)
            cmds = []
            for i, c in enumerate(channels):
                cmd_list = gen_commands_by_boundry_order(c, pens[i][1], i)
                # random.shuffle(cmd_list[5])
                # random.shuffle(cmd_list[6])
                # random.shuffle(cmd_list[7])
                # random.shuffle(cmd_list[8])
                cmds += cmd_list[0]+cmd_list[1]+cmd_list[2]+cmd_list[3]+cmd_list[4]+cmd_list[5]+cmd_list[6]+cmd_list[7]+cmd_list[8]
                # dst_img = np.zeros((64,96,3), np.uint8)
                # pens = [(255,255,255),(255,0,0),(0,255,0),(0,0,255),(255,255,0),(0,255,255),(255,0,255),(0,128,0,),(127,127,127),]
                # for cmd in cmds:
                #     pen = pens[cmd['bi']]
                #     dst_img[cmd['y']][cmd['x']] = pen
                # show_large('large', dst_img)
                # cv2.waitKey()

            # generate_tsv(color_reduced_img, os.path.join('pixel_scripts', main_name + '.tsv'))
            generate_csv(color_reduced_img, os.path.join('pixel_scripts', main_name + '.csv'))
    # cv2.waitKey()

if __name__ == "__main__":
    main()