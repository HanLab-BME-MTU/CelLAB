import numpy as np
import matplotlib.pyplot as plt
from skimage.feature import peak_local_max, blob_log
from skimage.segmentation import watershed
from skimage.measure import regionprops, label as relabel
from skimage.morphology import binary_closing, disk, remove_small_objects, binary_opening
from skimage.filters import threshold_otsu, threshold_local
from scipy.ndimage import distance_transform_edt, gaussian_filter
from scipy.spatial import cKDTree
from skimage import exposure
from skimage.color import label2rgb
from skimage.segmentation import find_boundaries
import cv2
import os
import glob
import random
from skfuzzy import cmeans


class CellADE_Cornealia:
    
    def __init__(self, input_image,verbosity_saving=False,log_min_sigma=5,log_max_sigma=30,log_num_sigma=15, log_threshold=0.01,fcm_method='global',fcm_threshold=0.4,min_area=30):
        
        self.input_image=input_image
        self.verbosity_saving=verbosity_saving
        self.log_max_sigma=log_max_sigma
        self.log_min_sigma=log_min_sigma
        self.log_threshold=log_threshold
        self.fcm_method=fcm_method
        self.log_num_sigma=log_num_sigma
        self.fcm_threshold=fcm_threshold
        self.min_area=min_area


        

    def preprocessing (self):
        # making grayscale
        H,W=self.input_image.shape[:2]
        self.H=H
        self.W=W

        input_image=self.input_image
        verbosity_saving=self.verbosity_saving
        
        if input_image.ndim==3:
            
            img_gray = cv2.cvtColor(input_image, cv2.COLOR_RGB2GRAY).astype(np.float32)

        else:
             img_gray=input_image.astype(np.float32)

        if verbosity_saving==False:
            del input_image

        # Normalization:
        norm_image= (img_gray- img_gray.min())/( img_gray.max()- img_gray.min()+ 1e-8)

        if verbosity_saving==False:
            del img_gray

        enhanced_image=exposure.equalize_adapthist(norm_image,clip_limit=0.03)

        if verbosity_saving==False:
            del norm_image

        
        self.enhanced_image=enhanced_image

    def blob_detection(self):
        
        # --- Blob Detection ---
        self.blobs=blob_log(self.enhanced_image, min_sigma=self.log_min_sigma, max_sigma=self.log_max_sigma, num_sigma=self.log_num_sigma, threshold=self.log_threshold)  # 
        
    
    
    def finding_global_bg(self):
        
        method=self.fcm_method
        H, W = self.enhanced_image.shape
        sqrt_2 = np.sqrt(2)
        fcm_threshold=self.fcm_threshold
                
        if method == 'global':
            image_fcm = self.enhanced_image.reshape(-1, 1).T.astype(np.float64) # we're converting to column vector; 
            cntr, u, _, _, _, _, _ = cmeans(data=image_fcm, c=2, m=2, error=0.005, maxiter=100, init=None)
            fg_index = np.argmax(cntr.flatten())
            global_fg = (u[fg_index] > fcm_threshold).reshape(self.H, self.W) # convertig back to matrix form ; 
            self.global_fg=global_fg

        if method == 'local':
            global_fg = np.zeros((self.H, self.W), dtype=bool)
            
            for i in range(len(self.blobs)):

                # finding blobs y,x and rarious
                y, x = int(self.blobs[i][0]), int(self.blobs[i][1])
                radius = int(self.blobs[i][2] * sqrt_2*1.5)

                # finding bounding box around each seed 
                y0, y1 = max(0, y - radius), min(H, y + radius)
                x0, x1 = max(0, x - radius), min(W, x + radius)

                # converting BB to circular for more accuracy 
                yy, xx = np.ogrid[y0:y1, x0:x1]
                circle_mask = (yy - y)**2 + (xx - x)**2 <= radius**2

                # making patch area image 
                patch_masked = np.where(circle_mask, self.enhanced_image[y0:y1, x0:x1], 0)
                image_fcm = patch_masked.reshape(-1, 1).T.astype(np.float64)

                # performing fcm on patch 
                cntr, u, _, _, _, _, _ = cmeans(data=image_fcm, c=2, m=2, error=0.005, maxiter=100, init=None)

                ## tresholding fcm output based on membership 
                fg_index = np.argmax(cntr.flatten())
                patch_fg = (u[fg_index] > fcm_threshold).reshape(patch_masked.shape) # u is one-column vector; we should convert it back to matrix form
                global_fg[y0:y1, x0:x1] |= (patch_fg & circle_mask) # we should attach the patch to the global fg 
        
            self.global_fg=global_fg
         
    def segmentation(self):
        
        from scipy.ndimage import distance_transform_edt
        from skimage.segmentation import watershed
        
       
        # step 1: we should convert the blob coordinates to the image form
        markers=np.zeros((self.H,self.W), dtype=np.int32)
        for i, (y,x,sigma) in enumerate(self.blobs):
            markers[int(y),int(x)]=i+1
        seed_mask = markers > 0
        dist_from_seeds = distance_transform_edt(~seed_mask)  # ~ inverts: distance TOWARD seeds
        self.labels = watershed(dist_from_seeds, markers=markers, mask=self.global_fg)

        from skimage.measure import regionprops
        objects=regionprops(self.labels)
        self.objects=[o for o in objects if o.area>self.min_area ] # filtering by minimum area

    def seg_one_frame(self):

        self.preprocessing()
        self.blob_detection()
        self.finding_global_bg()
        self.segmentation()

        return self.objects
        
    def plot_steps(self):
        fig, axes = plt.subplots(1, 4, figsize=(16, 4))

        # Step 1: input
        axes[0].imshow(self.input_image, cmap='gray')
        axes[0].set_title('Input')

        # Step 2: enhanced
        axes[1].imshow(self.enhanced_image, cmap='gray')
        axes[1].set_title('Enhanced')

        # Step 3: foreground + blobs
        axes[2].imshow(self.global_fg, cmap='gray')
        for y, x, s in self.blobs:
            axes[2].plot(x, y, 'r+', markersize=6)
        axes[2].set_title(f'FCM FG + Blobs ({len(self.blobs)})')

        # Step 4: final labels
        axes[3].imshow(label2rgb(self.labels, image=self.enhanced_image, bg_label=0))
        axes[3].set_title(f'Segmented ({len(self.objects)} cells)')

        for ax in axes:
            ax.axis('off')

        plt.tight_layout()
        plt.show()

    
