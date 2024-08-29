import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import DotLoader from "react-spinners/DotLoader";

function Booking() {
  const { id, screen } = useParams();
  const navigate = useNavigate("");
  const [{ theatre_name: theatreName, screens }, setCurTheatre] = useState("");
  const [bookingId, setBookingId] = useState();
  const [isLoading, setIsLoading] = useState(false);

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

  // async function refreshToken() {
  //   try {
  //     const res = await fetch(
  //       "https://homely-mia-hng-c4ac2199.koyeb.app/auth/user/refresh",
  //       {
  //         method: "POST",
  //         headers: {
  //           "Content-Type": "application/json",
  //         },
  //         credentials: "include",
  //       }
  //     );

  //     console.log(res);

  //     const data = await res.json();
  //     console.log(data);

  //     if (!res.ok) throw new Error(`Failed to refresh token: ${data.message}`);

  //     sessionStorage.setItem("accessToken", JSON.stringify(data.access_token));
  //   } catch (error) {
  //     console.log(error.message);
  //   }
  // }

  async function selectSeat(seatId) {
    try {
      setIsLoading(true);

      const accessToken = JSON.parse(sessionStorage.getItem("accessToken"));
      const res = await fetch(
        `https://homely-mia-hng-c4ac2199.koyeb.app/booking/`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${accessToken}`,
          },

          body: JSON.stringify({
            showtime_id: String(screens.at(0).showtimes.at(0).showtime_id),
            seats: [
              {
                seat_id: String(seatId),
              },
            ],
          }),
        }
      );

      console.log(res);
      if (!res.ok) throw new Error("There is error");

      const data = await res.json();
      if (!data) throw new Error("There error connecting");

      setBookingId(data.booking_id);

      navigate(`/${id}/${screen}/${bookingId}`);
    } catch (error) {
      console.log(error.message);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main className="relative">
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
      {isLoading && (
        <div className="absolute top-0 left-0 w-full h-full flex items-center justify-center bg-black bg-opacity-25 backdrop-blur">
          <DotLoader color="#c2410c" height={90} width={15} />
        </div>
      )}
    </main>
  );
}

export default Booking;
