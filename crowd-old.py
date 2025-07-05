import numpy as np
import cv2
import time
import argparse

def crowd (args):
    arg_input = args.input
    if arg_input in ['0','1','2','3']:
        arg_input = "http://61.211.241.239/nphMotionJpeg?Resolution=640x480&Quality=High"

    # input vid or cam
    cap = cv2.VideoCapture(arg_input)
    # load model
    net = cv2.dnn.readNet("yolov5n.onnx")
    classes = ["Orang"]

    frameSize = [1280, 640]
    cv2_fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out_path = f'{args.vname}.mp4'
    FPS1    = cap.get(cv2.CAP_PROP_FPS)
    out = cv2.VideoWriter(out_path,cv2_fourcc, FPS1, frameSize) # alternatif manual fps = 7


    while True:
        image = cap.read()[1]
        img = image.copy()
        if img is None:
            break

        start = time.time()
        blob = cv2.dnn.blobFromImage(img,scalefactor= 1/255,size=(640,640),mean=[0,0,0],swapRB= True, crop= False)
        net.setInput(blob)
        detections = net.forward()[0]
        classes_ids = []
        confidences = []
        boxes = []
        rows = detections.shape[0]

        img_width, img_height = img.shape[1], img.shape[0]
        x_scale = img_width/640
        y_scale = img_height/640

        for i in range(rows):
            row = detections[i]
            confidence = row[4]
            if confidence > 0.2:
                classes_score = row[5:]
                ind = np.argmax(classes_score)
                if classes_score[ind] > 0.2:
                    classes_ids.append(ind)
                    confidences.append(confidence)
                    cx, cy, w, h = row[:4]
                    x1 = int((cx- w/2)*x_scale)
                    y1 = int((cy-h/2)*y_scale)
                    width = int(w * x_scale)
                    height = int(h * y_scale)
                    box = np.array([x1,y1,width,height])
                    boxes.append(box)

        indices = cv2.dnn.NMSBoxes(boxes,confidences,0.2,0.2)
        cv2.putText(img, str(len(indices)), (40, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)

        for i in indices:
            x1,y1,w,h = boxes[i]
            label = classes[classes_ids[i]]
            conf = confidences[i]
            text = label + "{:.2f}".format(conf)
            cv2.circle(img, (int(x1+(w/2)), int(y1+(h/2))), min(w, h)//2, (0, 255, 0), 2)

        end = time.time()
        fps = f"FPS {int(1/(end-start))}"
        cv2.putText(img, fps, (450, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)
        
        img = cv2.resize(img, (640,640))
        image = cv2.resize(image, (640,640))
        im_h = cv2.hconcat([image, img])
        cv2.imshow("VIDEO",im_h)
        out.write(im_h)

        k = cv2.waitKey(1)
        if k == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    out.release()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--input', 
        type=str, 
        default='0',
        help= "path video OR cam 0,1,2"
    )

    parser.add_argument(
        '--vname', 
        type=str, 
        default='output_video',
        help= "video filename"
    )

    args = parser.parse_args()
    crowd(args)