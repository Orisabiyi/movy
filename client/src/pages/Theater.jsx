import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import DotLoader from "react-spinners/DotLoader";

function Theater() {
  const [theatres, setTheatres] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const { id } = useParams();

  useEffect(
    function () {
      async function getTheaters() {
        try {
          setIsLoading(true);
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
        } finally {
          setIsLoading(false);
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

      <section className="px-[3rem] py-[3rem] relative min-h-screen">
        <h2 className="mb-8 text-[3rem] font-extrabold">
          Theaters Showing Movies
        </h2>

        <div className="absolute top-[50%] left-[50%] translate-x-[-50%] translate-y-[-50%] h-full w-full flex items-center justify-center">
          {isLoading && <DotLoader color="#c2410c" height={90} width={15} />}
        </div>

        {theatres.length > 0 && (
          <div className="grid grid-cols-4 gap-[2rem]">
            {theatres?.map(({ theatre_name: theatreName, screens }) => (
              <figure
                key={theatreName}
                className="h-[35rem] flex flex-col border-[1.5px] border-orange-700 rounded-xl overflow-hidden"
              >
                <h3
                  className="h-[40%] flex justify-center items-center bg-orange-400 text-white text-[1.8rem] text-center font-bold"
                  style={{
                    background: "url(../../public/red-curtain.jpg)",
                    backgroundSize: "150%",
                    backgroundPosition: "top",
                  }}
                >
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
        )}
      </section>
    </main>
  );
}

export default Theater;
