function fakeLinkHover(row, focused) {
    if (focused) {
        rows = document.getElementsByTagName('tr');
        for (i = 0; i < rows.length; i++) {
            rows[i].style.backgroundColor = '';
        }
        row.style.backgroundColor = '#C45E5B';
        row.style.cursor = 'hand';
    } else {
        row.style.backgroundColor = '';
        row.style.cursor = 'pointer';
    }
};