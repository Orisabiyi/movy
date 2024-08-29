import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

function Booking() {
  const { id, screen } = useParams();
  const [{ theatre_name: theatreName, screens }, setCurTheatre] = useState("");

  useEffect(
    function () {
      async function getMovies() {
        try {
          const res = await fetch(
            `https://homely-mia-hng-c4ac2199.koyeb.app/movies/${id}/theatre`
          );
          const data = await res.json();

          const matchingTheatre = data.theatres.find(
            (theatre) => theatre.theatre_name === screen
          );

          setCurTheatre(matchingTheatre);
          // console.log(data.theatres);
        } catch (error) {
          console.log(error.message);
        }
      }

      getMovies();
    },
    [id, screen]
  );

  async function selectSeat(seatId) {
    try {
      const accessToken = JSON.parse(sessionStorage.getItem("accessToken"));

      const res = await fetch(
        `https://homely-mia-hng-c4ac2199.koyeb.app/booking`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },

          body: JSON.stringify({
            showtime_id: screens.at(0).showtimes.at(0).showtime_id,
            seats: [
              {
                seat_id: String(seatId),
              },
            ],
          }),
        }
      );

      console.log(screens.at(0).showtimes.at(0).showtime_id, seatId);
      const data = await res.json();

      if (!data) throw new Error("There error connecting");

      console.log(data);
    } catch (error) {
      console.log(error.message);
    }
  }

  return (
    <main>
      <section className="flex flex-col items-center justify-center gap-[4rem] min-h-screen px-[6rem] py-[3rem]">
        <div
          className="h-[20rem] w-full flex flex-col items-center justify-center text-[3rem] text-white font-semibold"
          style={{
            background: "url(/public/red-curtain.jpg)",
            backgroundSize: "cover",
            backgroundPosition: "top",
          }}
        >
          <span>{theatreName}</span>
          <span>Theatre</span>
        </div>
        <ul className="flex-1 grid grid-cols-10 gap-8 w-full">
          {screens &&
            screens[0].seats.map(
              ({ seat_number: seatNumber, seat_id: seatId, row }) => (
                <li
                  key={seatId}
                  className="flex flex-col items-center justify-center bg-orange-400 rounded-tr-[1.5rem] rounded-tl-[1.5rem] leading-6 text-[1.3rem] px-[1rem] py-[1.5rem] cursor-pointer hover:bg-white hover:border-[1px] hover:transition-all hover:border-orange-500"
                  onClick={() => selectSeat(seatId)}
                >
                  <span>{`Seat ${seatNumber}`}</span>
                  <span>{`Row ${row}`}</span>
                </li>
              )
            )}
        </ul>
      </section>
    </main>
  );
}

export default Booking;
