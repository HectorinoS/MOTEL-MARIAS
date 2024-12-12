document.addEventListener('DOMContentLoaded', function () {
    const searchForm = document.getElementById('search-form');
    const roomList = document.getElementById('room-list');

    searchForm.addEventListener('submit', function (e) {
        e.preventDefault();
        const formData = new FormData(searchForm);

        fetch('/search_rooms', {
            method: 'POST',
            body: formData
        })
            .then(response => response.json())
            .then(rooms => {
                roomList.innerHTML = '';
                if (rooms.length) {
                    rooms.forEach(room => {
                        const roomDiv = document.createElement('div');
                        roomDiv.innerHTML = `
                            <h3>Habitación ${room.number}</h3>
                            <p>Tipo: ${room.type}</p>
                            <p>Precio: $${room.price}/noche</p>
                            <button onclick="alert('Reserva no implementada aún')">Reservar</button>
                        `;
                        roomList.appendChild(roomDiv);
                    });
                } else {
                    roomList.innerHTML = '<p>No hay habitaciones disponibles para las fechas seleccionadas.</p>';
                }
            });
    });
});
