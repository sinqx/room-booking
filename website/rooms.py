from flask import (
    Blueprint,
    render_template,
    request,
    flash,
    redirect,
    url_for,
    jsonify,
)
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import and_, or_, Date
from .messages import get_all_messages
from .models import Room
from . import db

rooms = Blueprint("rooms", __name__)


@rooms.route("/", methods=["GET"])
@login_required
def home():
    """
    Отображает домашнюю страницу с информацией о забронированных комнатах пользователя.

    Returns:
        HTML-страница с информацией о забронированных комнатах.
    """
    currentDatetime = datetime.now()

    # Получение всех забронированных комнат пользователя, дата окончания которых позднее текущей даты
    my_rooms = Room.query.filter(
        Room.userId == current_user.id, Room.endDate > currentDatetime
    ).all()
    

    # Форматирование информации о забронированных комнатах в удобный для отображения вид
    myRooms = []
    for room in my_rooms:
        start_time = room.startDate.strftime("%Y-%m-%d -- %H:%M")
        end_time = room.endDate.strftime("%Y-%m-%d -- %H:%M")
        roomNumber = room.roomNumber
        booked_by_name = f"{room.user.firstName} {room.user.secondName}"
        event_name = room.conferenceTitle
        myRooms.append(
            {
                "roomNumber": roomNumber,
                "start_time": start_time,
                "end_time": end_time,
                "booked_by_name": booked_by_name,
                "event_name": event_name,
            }
        )
    messages = get_all_messages()

    return render_template(
        "home.html",
        user=current_user,
        current_datetime=currentDatetime,
        myRooms=myRooms,
        allMessages=messages,
    )


@rooms.route("/roomInfo/", methods=["GET"])
def get_room_info():
    """
    Возвращает информацию о забронированных временных слотах для указанной комнаты в указанное число.

    Args:
        roomNumber (int): Номер комнаты.
         reservationDate (datetime): Дата брони.


    Returns:
        JSON-объект с информацией о забронированных временных слотах.
    """

    room_number = int(request.args.get("roomNumber"))
    print(
        "--------------------------------"
    )
    reservation_date_str = str(request.args.get("reservationDate"))
    reservation_date = datetime.strptime(
        reservation_date_str, "%Y-%m-%dT%H:%M:%S.%fZ"
    ).date()

    booking_list = Room.query.filter(
        (Room.roomNumber == room_number),
        Room.endDate.cast(Date)  == reservation_date,
    ).all()

    occupied_times = []
    for booking in booking_list:
        start_time = booking.startDate.strftime("%Y-%m-%d%H:%M")
        end_time = booking.endDate.strftime("%Y-%m-%d%H:%M")
        booking_name = f"{booking.user.firstName} {booking.user.secondName}"
        event_name = booking.conferenceTitle
        occupied_times.append(
            {
                "start_time": start_time,
                "end_time": end_time,
                "booking_name": booking_name,
                "event_name": event_name,
            }
        )
    
    return jsonify({"occupied_times": occupied_times})


@rooms.route("/book_room", methods=["POST"])
@login_required
def book_room():
    """
    Бронирует комнату на указанный временной интервал.

    Args:
        roomNumber (str): Номер комнаты.
        startDate (str): Дата и время начала бронирования в формате "%Y-%m-%dT%H:%M".
        endDate (str): Дата и время окончания бронирования в формате "%Y-%m-%dT%H:%M".
        title (str): Название конференции.

    Returns:
        Перенаправление на домашнюю страницу.
    """
    room_number = request.form.get("roomNumber")
    start_date = datetime.strptime(request.form.get("startDate"), "%Y-%m-%dT%H:%M")
    end_date = datetime.strptime(request.form.get("endDate"), "%Y-%m-%dT%H:%M")
    conference_title = request.form.get("title")
    room_comment = request.form.get("comment")

    if end_date - start_date > timedelta(hours=24):
        flash("Нельзя бронировать зал более чем на 24 часа", category="error")
    elif end_date < start_date + timedelta(minutes=15):
        flash("Нельзя бронировать зал менее чем на 15 минут", category="error")
    else:
        existing_bookings = Room.query.filter(
            Room.roomNumber == room_number,
            or_(
                and_(
                    Room.startDate < end_date, Room.endDate > start_date
                ),  # Проверка перекрытия существующих броней
                and_(
                    Room.startDate == start_date, Room.endDate == end_date
                ),  # Проверка точного совпадения времени бронирования
                and_(
                    Room.startDate < start_date, Room.endDate > start_date
                ),  # Проверка частичного перекрытия броней
                and_(
                    Room.startDate < end_date, Room.endDate > end_date
                ),  # Проверка частичного перекрытия броней
            ),
        ).all()

        if existing_bookings:
            flash("Вы не можете забронировать на это время", category="error")
        else:
            new_booking = Room(
                roomNumber=room_number,
                conferenceTitle=conference_title,
                startDate=start_date,
                endDate=end_date,
                userId=current_user.id,
                comment=room_comment,
            )

            db.session.add(new_booking)
            db.session.commit()
            flash("Комната успешно забронирована", category="success")

    return redirect(url_for("rooms.home"))


@rooms.route("/cancel_book", methods=["DELETE"])
@login_required
def cancel_book():
    """
    Отменяет или завершает бронирование комнаты.

    Args:
        bookingId (str): Идентификатор бронирования.

    Returns:
        Перенаправление на домашнюю страницу.
    """
    booking_id = request.args.get("bookingId")
    booked_room = Room.query.filter_by(id=booking_id).first()

    if booked_room.userId == current_user.id:
        if datetime.now() < booked_room.startDate:
            db.session.delete(booked_room)
            flash("Бронь отменена", category="success")
        elif (
            datetime.now() > booked_room.startDate
            and datetime.now() < booked_room.endDate
        ):
            booked_room.endDate = datetime.now()
            flash("Бронь закончена", category="success")
        db.session.commit()
    else:
        flash("Не вы бронировали комнату", category="error")

    return redirect(url_for("rooms.home"))
