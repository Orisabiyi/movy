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

  return (
    <main>
      <section className="flex flex-col items-center justify-center gap-[2rem] h-screen px-[6rem] py-[3rem]">
        <div className="h-[20%] w-full flex flex-col items-center justify-center">
          {theatreName}
        </div>
        <ul className="flex-1 grid grid-cols-10 gap-8 w-full">
          {screens &&
            screens[0].seats.map(
              ({ seat_number: seatNumber, seat_id: seatId, row }) => (
                <li
                  key={seatId}
                  className="flex flex-col items-center justify-center bg-orange-400 rounded-tr-[1.5rem] rounded-tl-[1.5rem] leading-6 text-[1.3rem]"
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
