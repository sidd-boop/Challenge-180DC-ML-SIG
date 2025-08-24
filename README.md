The central strategy is to clean the images first with a specialized denoising model, followed by classifying the cleaned images with a strong image recognition model. Both models are trained from scratch based solely on the given dataset.

2. How the Pipeline Works
The code runs in a concise, linear fashion, divided into two distinct phases:

Data Preparation: The FlowerDataset class reads noisy and clean image pairs from the training directory. The whole dataset is then divided into a training set (80%) to learn from and a validation set (20%) to measure performance and to avoid overfitting.

Stage 1: Denoising:

The noisy/clean image pairs are used to train a U-Net model.

The model is trained to reduce the pixel-wise error (Mean Squared Error) between its prediction and the clean target image.

Subsequently, this U-Net is applied to denoise all images in the test_set, and the output is stored in the Denoised_Images directory.

Stage 2: Classification

A standalone ResNet-type classifier is trained on the clean images from the training set alone. Data augmentation (rotations, random flips, etc.) is utilized to robustify the model.

The model is taught to output the right flower category.

This classifier, after training, is then applied to predict the class for each of the Denoised_Images that are produced in Stage 1.

Final Output: The pipeline outputs the submission file required for test_labels.csv, where each test image is mapped to its predicted class label.

3. Model Architectures and Rationale
Stage 1: Denoising using U-Net
Architecture: The U-Net is an advanced encoder-decoder architecture.

Encoder (Contracting Path): This section behaves as a regular convolutional network. It gradually downsamples the image through MaxPool2d layers. Through this process, the model is able to learn the high-level context and features of the image (e.g., "this is a petal," "this is the center of a flower").

Decoder (Expanding Path): This section symmetrically upsamples feature maps with ConvTranspose2d layers to slowly build the image back up to its original resolution.

Skip Connections: This is the most important aspect of the U-Net. It connects the encoder feature maps directly to the corresponding decoder layers.  The connections give the decoder much-needed high-resolution spatial information that is lost by the downsampling process.

Reason for this Architecture: While a regular CNN is excellent at classification, it loses finer spatial details. To denoise, we must create a pixel-perfect output. The skip connections of U-Net are specifically designed to not lose fine details and thus work wonderfully well for image-to-image applications like denoising, segmentation, and restoration.

Stage 2: ResNet-style Classifier
Architecture: The classifier is a Residual Network (ResNet) implemented from scratch. Its basic building block is the ResidualBlock.

Residual Block: In a standard deep network, every layer needs to learn an entire transformation. In a ResNet, there is no need to learn the residual, or the small difference, from the input. It accomplishes this through a skip connection that adds the input of the block directly to the output.

Deep Structure: This architecture permits us to create very much deeper networks (our model has stacks of residual blocks) without having the "vanishing gradient" issue, where the learning signal becomes too diluted to train the early layers of the network.

Rationale for this Architecture: Deep networks are an advantage for image classification as they can learn a feature hierarchy, going from elementary edges to sophisticated shapes such as petals and leaves. ResNet architecture is an established and strong benchmark for image classification since its residual connections enable deep models to be trained stably, resulting in increased accuracy.



