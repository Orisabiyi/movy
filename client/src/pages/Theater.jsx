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

      <section className="px-[3rem] py-[6rem]">
        <h2 className="mb-8">Theaters Showing Movies</h2>
        <div className="grid grid-cols-4 gap-[2rem]">
          {theatres?.map(({ theatre_name: theatreName, screens }) => (
            <figure
              key={theatreName}
              className="h-[35rem] flex flex-col border-[1.5px] border-orange-700 rounded-xl overflow-hidden"
            >
              <h3 className="h-[40%] flex justify-center items-center bg-orange-400 text-orange-700 text-[1.8rem] text-center font-bold">
                {theatreName}
              </h3>
              <div className="flex flex-col flex-1 items-center justify-center">
                {screens.map(
                  ({
                    screen_name: screenName,
                    seat_remaining: seatRemaining,
                  }) => (
                    <Link
                      key={screenName}
                      className="flex flex-col gap-[.3rem] leading-5 px-[3rem] py-[1rem] font-semibold rounded-[50rem] border-orange-700 border-b-[2px] text-[1.3rem] hover:bg-orange-700 hover:text-white"
                    >
                      <span>Screen name: {screenName}</span>
                      <span>Seats Left: {seatRemaining}</span>
                    </Link>
                  )
                )}
              </div>
            </figure>
          ))}
        </div>
      </section>
    </main>
  );
}

export default Theater;
