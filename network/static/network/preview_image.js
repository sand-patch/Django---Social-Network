document.addEventListener('DOMContentLoaded', () => {
   document.getElementById('image').addEventListener('change', (e) => {
        const file = e.target.files[0];
        const preview_block = document.getElementById('preview_block');
        const preview = document.getElementById('preview');

        if (file) {
            const reader = new FileReader();
            reader.onload = function (e) {
                preview.src = e.target.result;
                preview_block.style.display = 'block';
            };
            reader.readAsDataURL(file);
        }
        else {
            preview_block.style.display = 'none';
            preview.removeAttribute('src');
        }
   }); 
});