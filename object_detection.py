import torch
import cv2


class ObjectDetection:
    """
    Loads Yolo5 model from pytorch hub and build custom inference
    :return: Custom trained YOLOv5 model.
    """

    def __init__(self):
        """
        Initializes the class.
        """
        self._count = 0
        self.model = self.load_model([0], 0.75, 0.50)
        self.classes = self.model.names
        self.device = "cpu"
        self.camera_number = 0
        self.frame = None

        # subject/observer pattern
        self._observers = []

    @property
    def count(self):
        return self._count

    @count.setter
    def count(self, value):
        self._count = value
        if value > 0:
            self.notify()

    def notify(self):
        """Notify observers of change."""
        for observer in self._observers:
            if self.count > 0:
                observer.update(self.frame, self.count)

    def attach(self, observer):
        """Add observer to list of observers."""
        if observer not in self._observers:
            self._observers.append(observer)

    def load_model(self, classes, conf, iou):
        """
        Loads Yolo5 model from pytorch hub and build custom inference
        :return: Custom trained YOLOv5 model.
        """
        model = torch.hub.load(
            "ultralytics/yolov5", "yolov5s", pretrained=True
        )
        model.classes = (
            classes  # by setting classes = [0], the model only detect person
        )
        model.conf = conf  # model confidence threshold
        model.iou = iou
        return model

    def score_frame(self, frame):
        """
        Takes a single frame as input, and scores the frame using yolo5 model.
        :param frame: input frame in numpy/list/tuple format.
        :return:
        Labels and Coordinates of objects detected by model in the frame.
        """
        self.model.to(self.device)
        frame = [frame]
        results = self.model(frame)

        labels, cord = results.xyxyn[0][:, -1], results.xyxyn[0][:, :-1]
        return labels, cord

    def class_to_label(self, x):
        """
        For a given label value, return corresponding string label.
        :param x: numeric label
        :return: corresponding string label
        """
        return self.classes[int(x)]

    def plot_boxes(self, results, frame):
        """
        Takes a frame and its results as input,
        and plots the bounding boxes and label on to the frame.
        :param results: contains labels and
         coordinates predicted by model on the given frame.
        :param frame: Frame which has been scored.
        :return: Frame with bounding boxes and labels ploted on it.
        """
        labels, cord = results
        objCounts = len(labels)
        x_shape, y_shape = (
            frame.shape[1],
            frame.shape[0],
        )  # .shape() access an image's property. return:
        # (rows, columns, channels)

        for i in range(objCounts):
            row = cord[i]
            if row[4] >= 0.2:
                x1, y1, x2, y2 = (
                    int(row[0] * x_shape),
                    int(row[1] * y_shape),
                    int(row[2] * x_shape),
                    int(row[3] * y_shape),
                )  # we need int instead float
                frame = cv2.rectangle(
                    frame, (x1, y1), (x2, y2), (125, 246, 55), 2
                )  # coordinates from top-left to bottom-right
                frame = cv2.putText(
                    img=frame,
                    text=f"{self.class_to_label(labels[i])} {i + 1}",
                    org=(x1, y1),
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale=0.9,
                    color=(125, 246, 55),
                    thickness=2,
                )  # takes coordinates of bottom left of text

        return frame, objCounts

    def get_counts(self):
        """
        This function returns number of object detects in each frame
        """
        return self.count

    def score_plot_frame(self, frame):
        """Score passed in frame."""
        results = self.score_frame(frame)
        scoredFrame, counts = self.plot_boxes(results, frame)
        return scoredFrame, counts

    def score_plot_image(self, path):
        """Score image on file path."""
        frame = cv2.imread(path)
        scoredFrame, counts = self.score_plot_frame(frame)
        return scoredFrame, counts

    def __call__(self):
        """
        This function is called when class is executed,
        it runs the loop to read the video frame by frame.
        """
        # depends on which camera a user would like to use, but
        # typically 0 is the default webcam on each laptop
        cap = cv2.VideoCapture(self.camera_number)

        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                break

            results = self.score_frame(frame)
            scoredFrame, counts = self.plot_boxes(results, frame)
            self.count = counts
            self.frame = scoredFrame

            ret, buffer = cv2.imencode(
                ".jpg", scoredFrame
            )  # encode the image format into streaming data
            # and assign it to memory cache. It is mainly used for
            # compressing image data format to facailitate network
            # transmission.
            scoredFrame = buffer.tobytes()

            # counts = [str(counts)]
            yield (
                b"--frame\r\nContent-Type: image/jpeg\r\n\r\n"
                + scoredFrame
                + b"\r\n"
            )  # concat frame one by one and show result


# detection = ObjectDetection()

# print(detection.get_counts())
