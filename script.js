const fileInput = document.getElementById('fileInput');
const canvas = document.getElementById('imageCanvas');
const ctx = canvas.getContext('2d');

let originalWidth, originalHeight; // Original dimensions of the image
let scaleRatio; // Scale ratio of the image
let selectionStart = null; // Start point of selection
let selectionEnd = null; // End point of selection
let currentImage = null; // To hold the current image

fileInput.addEventListener('change', function(e) {
    const file = e.target.files[0];
    const reader = new FileReader();
    reader.onload = function(event) {
        const img = new Image();
        img.onload = function() {
            currentImage = img; // Store the image for redrawing later
            originalWidth = img.naturalWidth;
            originalHeight = img.naturalHeight;

            const containerWidth = canvas.clientWidth;
            const aspectRatio = img.naturalWidth / img.naturalHeight;
            const containerHeight = containerWidth / aspectRatio;
            scaleRatio = containerWidth / img.naturalWidth;

            canvas.width = containerWidth;
            canvas.height = containerHeight;

            ctx.drawImage(img, 0, 0, containerWidth, containerHeight);
        };
        img.src = event.target.result;
    };
    reader.readAsDataURL(file);
});

canvas.addEventListener('click', function(e) {
    const rect = canvas.getBoundingClientRect();
    const scaleX = originalWidth / rect.width;
    const scaleY = originalHeight / rect.height;
    const x = (e.clientX - rect.left) * scaleX; // Convert canvas coordinate to original image scale
    const y = (e.clientY - rect.top) * scaleY;

    if (!selectionStart) {
        selectionStart = { x: Math.round(x), y: Math.round(y) };
    } else {
        selectionEnd = { x: Math.round(x), y: Math.round(y) };

        console.log(`Selection coordinates on original image - Start (X: ${selectionStart.x}, Y: ${selectionStart.y}), End (X: ${selectionEnd.x}, Y: ${selectionEnd.y})`);
        visualizeSelection(); // Visualize the selection on the canvas
        selectionStart = null; // Reset for the next selection
    }
});

function visualizeSelection() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(currentImage, 0, 0, canvas.width, canvas.height);

    const startX = selectionStart.x * scaleRatio;
    const startY = selectionStart.y * scaleRatio;
    const width = (selectionEnd.x - selectionStart.x) * scaleRatio;
    const height = (selectionEnd.y - selectionStart.y) * scaleRatio;

    ctx.beginPath();
    ctx.strokeStyle = 'green';
    ctx.lineWidth = 2;
    ctx.rect(startX, startY, width, height);
    ctx.stroke();
}
