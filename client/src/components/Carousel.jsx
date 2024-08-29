import { useEffect, useState } from "react";
import { ClipLoader } from "react-spinners";

export default function Carousel() {
  const [movies, setMovies] = useState([]);

  useEffect(function () {
    async function getMovies() {
      try {
        const res = await fetch("https://homely-mia-hng-c4ac2199.koyeb.app/");
        const data = await res.json();
        const limitedMovies = data.results.slice(0, 5);
        setMovies(limitedMovies);
      } catch (error) {
        console.log(error.message);
      }
    }

    getMovies();
  }, []);

  return (
    <>
      <div className="h-full flex items-center justify-center">
        {movies.length > 0 ? (
          movies.map((movie) => (
            <figure
              key={movie.title}
              className="keen-slider__slide w-full h-full"
            >
              <img
                src={movie.poster_path}
                alt="movie image"
                className="block w-full h-full"
              />
            </figure>
          ))
        ) : (
          <ClipLoader color="#c2410c" height={90} width={15} />
        )}
      </div>
    </>
  );
}
