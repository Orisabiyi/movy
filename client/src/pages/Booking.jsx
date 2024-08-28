import { useEffect } from "react";
import { useParams } from "react-router-dom";

function Booking() {
  const { id } = useParams();
  useEffect(
    function () {
      async function getMovies() {
        try {
          const res = await fetch(
            `https://homely-mia-hng-c4ac2199.koyeb.app/movies/${id}/theatre`
          );
          const data = await res.json();

          console.log(data);
        } catch (error) {
          console.log(error.message);
        }
      }

      getMovies();
    },
    [id]
  );

  return (
    <main>
      <section>
        <div></div>
        <div></div>
      </section>
    </main>
  );
}

export default Booking;
