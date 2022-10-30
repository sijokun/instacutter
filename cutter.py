from PIL import Image


def cut_to_parts(image):
    parts = []
    w, h = image.size
    n = 2
    s = w/n
    while s/h > 1.91/1 or s/h < 4/5:
        n += 1
        s = w / n

        if n >= 10:
            return None, None, False

    for i in range(n):
        parts.append(image.crop((s*i, 0, s*(i+1), h)))

    full_img = Image.new('RGB', (int(s), h), (255, 255, 255))
    full_img.paste(image.resize((int(s), int(s/w*h))), (0, int((h-(s/w*h))/2)))

    return parts, full_img, True


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    img = Image.open("./img.jpg")
    p, full = cut_to_parts(img)
    #
    # for i in range(len(p)):
    #     p[i].save(f'{i}.jpg')
    # full.save('full.jpg')


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
