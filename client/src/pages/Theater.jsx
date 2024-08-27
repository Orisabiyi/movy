import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

function Theater() {
  const [theatres, setTheatres] = useState([]);
  const { id } = useParams();

  useEffect(
    function () {
      async function getTheaters() {
        try {
          const res = await fetch(
            `https://homely-mia-hng-c4ac2199.koyeb.app/movies/${id}/theatre`
          );
          const data = await res.json();

          if (!data)
            throw new Error("There is an error connecting to the internet");

          setTheatres(data.theatres);
          console.log(data.theatres);
        } catch (error) {
          console.log(error);
        }
      }

      getTheaters();
    },
    [id]
  );

  return (
    <main>
      <nav className="flex items-center gap-[2rem] px-[3rem] py-[1.5rem]">
        <figure className="text-[2.5rem] text-white font-semibold bg-orange-700 p-[1rem] rounded-lg">
          <Link to="/">M</Link>
        </figure>
        <p className="font-bold leading-10 text-orange-700 text-[3rem]">Movy</p>
      </nav>

      <section>
        <h2>Theaters Showing Movies</h2>
        <div className="">
          {theatres?.map(({ theatre_name: theatreName }) => (
            <figure key={theatreName}>
              <h3>{theatreName}</h3>
              <div></div>
            </figure>
          ))}
        </div>
      </section>
    </main>
  );
}

export default Theater;
