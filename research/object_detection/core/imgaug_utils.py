import imgaug.augmenters as iaa
from imgaug.augmentables.bbs import BoundingBox, BoundingBoxesOnImage
from tensorflow.python.framework.ops import EagerTensor
import tensorflow as tf
import numpy as np

augseq = iaa.Sequential([
    iaa.Crop(px=(0, 16)), # crop images from each side by 0 to 16px (randomly chosen)
    iaa.Fliplr(0.5), # horizontally flip 50% of the images
    iaa.GaussianBlur(sigma=(0, 3.0)) # blur images with a sigma of 0 to 3.0
], random_order=True)
# """ <- Comment Guide

@tf.function
def augment(image, boxes):
    image_np = image.numpy().astype(np.uint8) if type(image) == EagerTensor else image
    boxes_np = boxes.numpy() if type(boxes) == EagerTensor else boxes
    width, height, _ = image_np.shape
    bbs = []
    for i in range(len(boxes_np)):
        box = boxes_np[i]
        # ymin, xmin, ymax, xmax = tf.unstack(box) #Cast tensor to numpy!
        ymin, xmin, ymax, xmax = box.numpy()
        bbs.append(BoundingBox(
            x1=xmin*width, y1=ymin*height,
            x2=xmax*width, y2=ymax*height,))
    bbs = BoundingBoxesOnImage(bbs, shape=image_np.shape)
    image_aug, bbs_aug = augseq(image=image_np, bounding_boxes=bbs) # float np.ndarray
    bbs_aug = bbs_aug.remove_out_of_image().clip_out_of_image()
    
    boxes_aug = []
    for bb in bbs_aug:
        boxes_aug.append([bb.y1/height, bb.x1/width, bb.y2/height, bb.x2/width])
    boxes_aug = np.array(boxes_aug)
    
    merge = np.concatenate((image_aug, boxes_aug), axis=None)
    # return merge
    return image_aug, boxes_aug