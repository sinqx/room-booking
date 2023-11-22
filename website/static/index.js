async function roomInfo(roomNumber, reservationDate) {
  try {
    const response = await fetch(
      `/roomInfo/?roomNumber=${roomNumber}&reservationDate=${reservationDate}`
    );
    const data = await response.json();
    const bookingInfo = data.occupied_times;
    const bookingInfoContainer = document.querySelector(
      `#bookingInfo${roomNumber}`
    );
    const occupiedTimesElement = bookingInfoContainer.querySelector(
      `#occupiedTimes${roomNumber}`
    );

    occupiedTimesElement.innerHTML = "";

    if (bookingInfo.length > 0) {
      bookingInfo.forEach((booking) => {
        const occupiedTime = document.createElement("li");
        occupiedTime.style.display = "flex";

        const startTime = new Date(booking.start_time);
        const endTime = new Date(booking.end_time);

        const formattedStartTime = new Intl.DateTimeFormat("ru-RU", {
          hour: "numeric",
          minute: "numeric",
        }).format(startTime);

        const formattedEndTime = new Intl.DateTimeFormat("ru-RU", {
          hour: "numeric",
          minute: "numeric",
        }).format(endTime);

        const currentDateTime = new Date();

        const timeRange = document.createElement("span");
        timeRange.innerHTML = `${formattedStartTime} - ${formattedEndTime}`;

        if (currentDateTime >= startTime && currentDateTime <= endTime) {
          timeRange.style.backgroundColor = "orange";
        } else if (currentDateTime > endTime) {
          timeRange.style.backgroundColor = "red";
        } else {
          timeRange.style.backgroundColor = "green";
        }

        timeRange.style.borderRadius = "30px";
        timeRange.style.padding = "3px";
        timeRange.style.color = "white";
        timeRange;
        occupiedTime.innerHTML = `
        <div>
          <strong>${booking.event_name}</strong><br>
          Продолжительность:<br>
          ${timeRange.outerHTML}<br>
          Забронированно на: <br> ${booking.booking_name}<br>
          </div>
        `;
        if (booking.comment.length > 0) {
          console.log(booking.comment);
          occupiedTime.innerHTML += `<button
          type="button"
          class="btn btn-xs"
          data-bs-toggle="popover"
          data-bs-title="Информация:"
          data-bs-content="${booking.comment}"
          data-bs-placement="right"
          >
          <img
                  width="25"
                  height="25"
                  src="../static/info_icon.svg"
                  alt="Info Icon"
                />
        </button>`;
        }
        const newButton = occupiedTime.querySelector(
          "button[data-bs-toggle='popover']"
        );
        const popover = new bootstrap.Popover(newButton);

        newButton.addEventListener("click", function () {
          popover.toggle();
        });
        occupiedTimesElement.appendChild(occupiedTime);
      });
    } else {
      const noBookingsMessage = document.createElement("p");
      noBookingsMessage.textContent = "Броней нет.";
      occupiedTimesElement.appendChild(noBookingsMessage);
    }
  } catch (error) {
    console.error("Ошибка:", error);
  }
}

function messageInfo(messageId) {
  fetch(`/get_message_info?messageId=${messageId}`, {
    method: "GET",
  })
    .then((response) => response.json())
    .then((data) => {
      // Полученный объект сообщения
      const message = data.message;

      // Пример обновления контейнера с текстом сообщения
      const messageContainer = document.getElementById("messageContainer");
      if (messageContainer) {
        messageContainer.message = message;
      }
    })
    .catch((error) => {
      console.error("Ошибка при получении сообщения:", error);
    });
}

// Получение информации о бронировании комнаты и сообщениях
document.addEventListener("DOMContentLoaded", function () {
  // Получаем все кнопки зала
  const currentDateElement = document.getElementById("currentDate");
  let currentDate = new Date();

  function updateRoomInfo() {
    const buttonNames = [
      "Конференц-зал",
      "Компьютерный зал",
      "Зал для презентаций",
      "Аудитория",
      "Мультимедийный зал",
      "Тренинг-зал",
    ];

    const formattedDate = currentDate.toISOString();
    for (let i = 0; i < buttonNames.length; i++) {
      roomInfo(i, formattedDate);
    }
  }

  const messageButtons = document.querySelectorAll(".message-button");
  messageButtons.forEach(function (button) {
    button.addEventListener("click", function () {
      const messageId = this.dataset.messageId;
      console.log(messageId);
      messageInfo(messageId);
    });
  });

  const prevDateButton = document.getElementById("prevDate");
  prevDateButton.addEventListener("click", () => {
    currentDate.setDate(currentDate.getDate() - 1);
    updateCurrentDate();
    updateRoomInfo();
  });

  // Обработчик события для кнопки "Следующая дата"
  const nextDateButton = document.getElementById("nextDate");
  nextDateButton.addEventListener("click", () => {
    currentDate.setDate(currentDate.getDate() + 1);
    updateCurrentDate();
    updateRoomInfo();
  });

  updateCurrentDate();
  updateRoomInfo();

  function updateCurrentDate() {
    currentDateElement.textContent = currentDate.toLocaleDateString();
  }
});

let popoverTriggerList = [].slice.call(
  document.querySelectorAll('[data-bs-toggle="popover"]')
);
let popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
  return new bootstrap.Popover(popoverTriggerEl);
});
