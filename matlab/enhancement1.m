% Enhancement Stage 1
%
% Input: image
%
% Output:   I0_eq   -> Enhanced
%           I0_eq2  -> Enhanced + Vascular Enhancement

% Enhancement Factor in range  [0  255]
    E_factor = 50;


% Frangi filter for Vessels
    addpath 'D:\Doctorado\EyeSpot\codigo\frangi_filter';

% File locations        
    directory = 'D:\Doctorado\EyeSpot\diaretdb1_v_1_1\resources\images\ddb1_fundusimages\';
    name_file = 'image047.png';
    
% Read the image
    I0 = imread([directory,name_file]);

% Green channel
    I = I0(:,:,2);    
    
% Mask detection to crop the image.
%   Morphologic operations can be done with openCV:
    % cv2.erode(), cv2.dilate()
    mask = I>10; %I>min(I(:));
    mask = bwmorph(mask,'erode',5);
    mask = bwmorph(mask,'dilate',5);
    
% Resize the image    
    [fil,col] = find(mask==1); % size of the image
    rect = [min(fil(:)) max(fil(:)) min(col(:))  max(col(:))]; % rectangle [min_row max_row min_col max_col]    
    
    I0 = I0(rect(1):rect(2),rect(3):rect(4),:); % resize
    I = I0(:,:,2);                              % Green channel
    
% Histogram equalization of green channel
    % Contrast-limited Adaptive Histogram Equalization (CLAHE)
    % cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    %
    % WARNING: clipLimit and so depends on the intensity levels of the
    % image. In matlab we're doing this with it normalized to 1, clipLimit
    % = 0.01 by default.
    I_eq = adapthisteq(I);  
    
% Frangi filter with following options:
    % This function requires:
    % 1.- Hessian2D
    % 2.- eig2image
    % Actually, we can avoid eig2image and remove ALLangles interactions
    Options = struct('FrangiScaleRange', [2 6], 'FrangiScaleRatio', 0.5, 'FrangiBetaOne', 0.5, 'FrangiBetaTwo', 15, 'verbose',true,'BlackWhite',true);
    [outIm,whatScale,Direction] = FrangiFilter2D(double(I_eq),Options);    
    
% Equalization of channels    
    I0_eq = zeros(size(I0),'uint8');
    I0_eq(:,:,1) = adapthisteq(I0(:,:,1));
    I0_eq(:,:,2) = I_eq;
    I0_eq(:,:,3) = adapthisteq(I0(:,:,3));        
    
% Vascular enhancement
    I0_eq2 = zeros(size(I0));    
    for conta = 1:3
        aux = uint8(I0_eq(:,:,conta)) - uint8(E_factor*outIm);
        aux(aux<0) = 0;        
        I0_eq2(:,:,conta) = aux;
    end        
    
figure(10);
imshow(I0,[]);

figure(20);
imshow([I0_eq I0_eq2],[]);






