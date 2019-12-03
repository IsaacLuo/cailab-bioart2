import cv2
import os
import numpy as np
import random

pens = [((230,230,230), 'A1'), ((50,50,50), 'A2'), ((200,50,50), 'A3')]
g_width=96
g_height=64

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
        for pen in pens:
            for i in range(height):
                for j in range(width):
                    if img[i][j][0] == pen[0][0] and img[i][j][1] == pen[0][1] and img[i][j][2] == pen[0][2]:
                        x, y = img_coord_to_pisycal_coord(j,i,width, height)
                        fp.write('Source1\t{0}\t{1}\tTarget1\t{2}\t{3}\t'.format(pen[1][0], pen[1][1:], y, x))
            fp.write('\n')

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

def generate_tsv2(cmds, main_name, max_cmd_count):
    file_count = 0
    same_color_count=0
    max_bi_count=[1,1,1,1,1,2,2,3,8]
    bi_count=1
    while True:
        with open(os.path.join('pixel_scripts', '{}_{}.tsv'.format(main_name, file_count)), 'w') as fp:
            fp.write('Source1\tMWP\t96\tSource\n')
            fp.write('Target1\tSBS\tnone\tTarget\n')
            cmd_count = 0
            cmd_row_count = 0
            while cmd_row_count < max_cmd_count:
                current_cmd_count = file_count*max_cmd_count + cmd_count
                if current_cmd_count >= len(cmds):
                    break
                cmd = cmds[current_cmd_count]
                x, y = img_coord_to_pisycal_coord(cmd['x'],cmd['y'],g_width, g_height)
                fp.write('Source1\t{0}\t{1}\tTarget1\t{2}\t{3}'.format(cmd['src'][0], cmd['src'][1:], y, x))
                if current_cmd_count < len(cmds)-1 and cmd['src'] == cmds[current_cmd_count+1]['src'] and cmd['bi'] == cmds[current_cmd_count+1]['bi'] and bi_count < max_bi_count[cmd['bi']]:
                    bi_count+=1
                    fp.write('\t')
                else:
                    fp.write('\n')
                    bi_count = 1
                    cmd_row_count+=1
                cmd_count+=1
            else:
                file_count+=1
                continue
            break

def generate_tsv3(cmds, main_name, max_cmd_count):
    file_count = 0
    same_color_count=0
    # max_bi_count=[1,1,1,1,1,2,2,3,8]
    max_bi_count=[100,100,100,100,100,100,100,100,100]
    bi_count=1
    while True:
        with open(os.path.join('pixel_scripts', '{}_{}.tsv'.format(main_name, file_count)), 'w') as fp:
            fp.write('Source1\tSBS\tnone\tSource\n')
            fp.write('Source2\tSBS\tnone\tSource\n')
            fp.write('Target1\tSBS\tnone\tTarget\n')
            cmd_count = 0
            cmd_row_count = 0
            while cmd_row_count < max_cmd_count:
                current_cmd_count = file_count*max_cmd_count + cmd_count
                if current_cmd_count >= len(cmds):
                    break
                cmd = cmds[current_cmd_count]
                channel_id = cmd['channel_id']
                x, y = img_coord_to_pisycal_coord(cmd['x'],cmd['y'],g_width, g_height)
                # fp.write('Source1\t{0}\t{1}\tTarget1\t{2}\t{3}'.format(cmd['src'][0], cmd['src'][1:], y, x))
                fp.write('Source{}\t{}\t{}\tTarget1\t{}\t{}'.format(channel_id+1, y, x, y, x))
                if current_cmd_count < len(cmds)-1 and cmd['src'] == cmds[current_cmd_count+1]['src'] and cmd['bi'] == cmds[current_cmd_count+1]['bi'] and bi_count < max_bi_count[cmd['bi']]:
                    bi_count+=1
                    fp.write('\t')
                else:
                    fp.write('\n')
                    bi_count = 1
                    cmd_row_count+=1
                cmd_count+=1
            else:
                file_count+=1
                continue
            break

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
                random.shuffle(cmd_list[5])
                random.shuffle(cmd_list[6])
                random.shuffle(cmd_list[7])
                random.shuffle(cmd_list[8])
                cmds += cmd_list[0]+cmd_list[1]+cmd_list[2]+cmd_list[3]+cmd_list[4]+cmd_list[5]+cmd_list[6]+cmd_list[7]+cmd_list[8]
                # dst_img = np.zeros((64,96,3), np.uint8)
                # pens = [(255,255,255),(255,0,0),(0,255,0),(0,0,255),(255,255,0),(0,255,255),(255,0,255),(0,128,0,),(127,127,127),]
                # for cmd in cmds:
                #     pen = pens[cmd['bi']]
                #     dst_img[cmd['y']][cmd['x']] = pen
                # show_large('large', dst_img)
                # cv2.waitKey()

            # generate_tsv(color_reduced_img, os.path.join('pixel_scripts', main_name + '.tsv'))
            generate_tsv3(cmds, main_name, 5000)
    # cv2.waitKey()

if __name__ == "__main__":
    main()