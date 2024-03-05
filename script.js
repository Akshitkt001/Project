async function processVideo() {
    const videoInput = document.getElementById('videoInput').files[0];
    if (!videoInput) {
        alert('Please select a video file.');
        return;
    }

    const formData = new FormData();
    formData.append('video', videoInput);

    const uploadProgress = document.getElementById('uploadProgress');

    const response = await fetch('/process_video', {
        method: 'POST',
        body: formData,
        onUploadProgress: (progressEvent) => {
            const { loaded, total } = progressEvent;
            uploadProgress.value = (loaded / total) * 100;
        }
    });

    if (response.ok) {
        const result = await response.json();
        document.getElementById('output').innerText = result.message;
        
        const processingProgress = document.getElementById('processingProgress');
        processingProgress.value = 100; // Assuming video processing is complete

        const videoContainer = document.getElementById('videoContainer');
        videoContainer.style.display = 'block';

        const processedVideo = document.getElementById('processedVideo');
        processedVideo.src = result.video_url;
    } else {
        alert('Error processing video.');
    }
}
