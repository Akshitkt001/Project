async function processVideo() {
    const videoInput = document.getElementById('videoInput').files[0];
    if (!videoInput) {
        alert('Please select a video file.');
        return;
    }

    const formData = new FormData();
    formData.append('video', videoInput);

    const response = await fetch('/process_video', {
        method: 'POST',
        body: formData
    });

    if (response.ok) {
        const result = await response.json();
        document.getElementById('output').innerText = result.message;
    } else {
        alert('Error processing video.');
    }
}
