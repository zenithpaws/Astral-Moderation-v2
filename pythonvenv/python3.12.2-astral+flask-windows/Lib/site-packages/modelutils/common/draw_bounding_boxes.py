import argparse
import pathlib
import PIL.Image
import PIL.ImageDraw

from utils import read_input_npy


def draw_boxes(image_filepath, output_image_filepath, predictions, threshold=0.1):
    """Draw the predicted bounding boxes.
    Args:
        predictions: A list of bounding boxes. Each boundign box representation is [<label>, <probability>, <x>, <y>, <x2>, <y2>]. All coordinates should be normalized.
    """
    COLOR_CODES = ["black", "brown", "red", "orange", "yellow", "green", "blue", "violet", "grey", "white"]

    image = PIL.Image.open(image_filepath)
    w, h = image.size
    draw = PIL.ImageDraw.Draw(image)
    for prediction in predictions:
        if prediction[1] >= threshold:
            color = COLOR_CODES[prediction[0] % len(COLOR_CODES)]
            x, y = prediction[2] * w, prediction[3] * h
            x2, y2 = prediction[4] * w, prediction[5] * h
            width = 2 if prediction[1] > 0.5 else 1
            draw.rectangle(((x, y), (x2, y2)), outline=color, width=width)
            draw.text((x + 2, y + 2), f"{prediction[0]} ({int(prediction[1]*100)}%)", fill=color)
            print(f"label: {prediction[0]}, prob: {prediction[1]:.5f}, box: ({prediction[2]:.5f}, {prediction[3]:.5f}), ({prediction[4]:.5f}, {prediction[5]:.5f})")

    image.save(output_image_filepath)


def draw_bounding_boxes(image_filepath, output_filepath, is_yxyx):
    input_data = read_input_npy(None)
    input_data = input_data.item()

    detected_boxes = input_data['detected_boxes'][0]
    detected_classes = input_data['detected_classes'].flatten()
    detected_scores = input_data['detected_scores'].flatten()
    num_detections = int(input_data['num_detections']) if 'num_detections' in input_data else len(detected_boxes)

    predictions = []
    for i in range(num_detections):
        predictions.append([int(detected_classes[i]), detected_scores[i], *detected_boxes[i]])

    if is_yxyx:  # Convert (x_min, y_min, x_max, y_max) => (y_min, x_min, y_max, x_max).
        predictions = [[p[0], p[1], p[3], p[2], p[5], p[4]] for p in predictions]

    draw_boxes(image_filepath, output_filepath, predictions)
    print(f"Saved to {output_filepath}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('image_filepath', type=pathlib.Path)
    parser.add_argument('output_filepath', type=pathlib.Path)
    parser.add_argument('--yxyx', action='store_true', help="The box format is [y_min, x_min, y_max, x_max]")

    args = parser.parse_args()
    draw_bounding_boxes(args.image_filepath, args.output_filepath, args.yxyx)


if __name__ == '__main__':
    main()
