document.addEventListener('DOMContentLoaded', function() {
    const minimizeBtn = document.getElementById('minimize-btn');
    const maximizeBtn = document.getElementById('maximize-btn');
    const closeBtn = document.getElementById('close-btn');
    const tableContainer = document.getElementById('table-container');
    const tableContent = document.getElementById('table-content');
    let isFullScreen = false;

    minimizeBtn.addEventListener('click', function() {
        tableContainer.style.height = '50px';
        tableContent.style.display = 'none';
    });

    maximizeBtn.addEventListener('click', function() {
        if (isFullScreen) {
            tableContainer.classList.remove('full-screen');
            tableContent.style.display = 'block';
            tableContainer.style.height = '200px';
            isFullScreen = false;
        } else {
            tableContainer.classList.add('full-screen');
            tableContent.style.display = 'block';
            isFullScreen = true;
        }
    });

    closeBtn.addEventListener('click', function() {
        tableContainer.style.display = 'none';
    });
});
