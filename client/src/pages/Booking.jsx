import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

function Booking() {
  const { id, screen } = useParams();
  const [{ theatre_name: theatreName }, setCurTheatre] = useState("");

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
      <section className="flex flex-col h-screen">
        <div className="h-[40%]">{theatreName}</div>
        <div></div>
      </section>
    </main>
  );
}

export default Booking;
