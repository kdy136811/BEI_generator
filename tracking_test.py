import cv2
import json

def Video2Images(video, frame_list):
    video_images = []
    vc = cv2.VideoCapture(video)

    c = 1
    frame = 0
    ret = True
    while ret:
        ret, video_frame = vc.read()
        if(c == frame_list[frame]):
            video_images.append(video_frame)
            if frame < len(frame_list)-1:
                frame = frame+1
        c = c+1

    vc.release()
    
    return video_images

if __name__ == '__main__':
    with open('../data/test_video_1_1_hoop_pos.json', 'r', encoding='utf-8') as f:
        hoop = json.load(f)
    print(len(hoop))
    
    #Get the frames detected with hoop
    frame_list = []
    for i in range(len(hoop)):
        frame_list.append(hoop[i]['index']+1)
    filename = '../data/test_video_1_1.mp4'
    images = Video2Images(filename, frame_list)

    #Cut the hoops region
    crop_images = []
    for i in range(len(hoop)):
        bbox = hoop[i]['box']
        x = bbox[0]
        y = bbox[1]
        w = bbox[2]
        h = bbox[3]
        cimg = images[i][y:y+h, x:x+w]
        crop_images.append(cimg)

    #cv2.imshow('img', crop_images[0])
    #cv2.waitKey(0)

    size_w = 340
    size_h = 410
    print(len(crop_images))
    videoWriter = cv2.VideoWriter('./hoop.mp4', cv2.VideoWriter_fourcc(*'DIVX'), 30, (size_w, size_h))
    for img in crop_images:
        img = cv2.resize(img, (size_w, size_h))
        videoWriter.write(img)
    videoWriter.release()