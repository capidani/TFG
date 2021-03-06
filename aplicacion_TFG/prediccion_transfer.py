'''
Autor           :Adil Moujahid
Modificacion    :Daniel Capitan
'''

import os
import glob
import cv2
import caffe
import lmdb
import numpy as np
from caffe.proto import caffe_pb2

caffe.set_mode_gpu() 

#Size of images
IMAGE_WIDTH = 227
IMAGE_HEIGHT = 227

'''
Tratamiento de imagen
'''

def transform_img(img, img_width=IMAGE_WIDTH, img_height=IMAGE_HEIGHT):

    #Histogram Equalization
    img[:, :, 0] = cv2.equalizeHist(img[:, :, 0])
    img[:, :, 1] = cv2.equalizeHist(img[:, :, 1])
    img[:, :, 2] = cv2.equalizeHist(img[:, :, 2])

    #Image Resizing
    img = cv2.resize(img, (img_width, img_height), interpolation = cv2.INTER_CUBIC)

    return img


'''
Abrir imagenes, modelo y pesos
'''
#Read mean image
mean_blob = caffe_pb2.BlobProto()
with open('/home/user_cudnn/aplicacionTFG/mean.binaryproto') as f:
    mean_blob.ParseFromString(f.read())
mean_array = np.asarray(mean_blob.data, dtype=np.float32).reshape(
    (mean_blob.channels, mean_blob.height, mean_blob.width))


#Read model architecture and trained model's weights
net = caffe.Net('/home/user_cudnn/aplicacionTFG/modelos/transfer_learning/cell_deploy.prototxt',
                '/home/user_cudnn/aplicacionTFG/modelos/tfg_modelo_transfer.caffemodel',
                caffe.TEST)

#Define image transformers
transformer = caffe.io.Transformer({'data': net.blobs['data'].data.shape})
transformer.set_mean('data', mean_array)
transformer.set_transpose('data', (2,0,1))

'''
Predicciones
'''
#Reading image paths
test_img_paths = [img_path for img_path in glob.glob("/home/user_cudnn/aplicacionTFG/imagenes/test/*tiff")]

#Making predictions
test_ids = []
preds = []
for img_path in test_img_paths:
    img = cv2.imread(img_path, cv2.IMREAD_COLOR)
    img = transform_img(img, img_width=IMAGE_WIDTH, img_height=IMAGE_HEIGHT)
    
    net.blobs['data'].data[...] = transformer.preprocess('data', img)
    out = net.forward()
    pred_probas = out['prob']

    test_ids = test_ids + [img_path.split('/')[-1][:-4]]
    preds = preds + [pred_probas.argmax()]



    print img_path
    #print pred_probas
    #print pred_probas.argmax()
    if pred_probas.argmax()==1:
        print 'La celula es ALTO GRADO'
    else:
        print 'La celula es BENIGNA'
    print '-------'

'''
Crear fichero de resultados
'''
with open("resultado.csv","w") as f:
    f.write("id,tipo,label\n")
    for i in range(len(test_ids)):
        if preds[i]==1:
            tipo = 'ALTO GRADO'
        else:
            tipo ='BENIGNA'

        f.write(str(test_ids[i])+","+str(tipo)+","+str(preds[i])+"\n")
f.close()
