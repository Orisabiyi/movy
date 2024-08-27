import { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";

import { Link } from "react-router-dom";

function MovieDetails() {
  const { search } = useLocation();
  const searchId = search.slice(1, search.length);

  const [
    {
      title,
      tag_line: tagline,
      trailer_link: trailer,
      description,
      release_date: releaseDate,
      genres,
      starring,
    },
    setMoviesData,
  ] = useState({});

  useEffect(
    function () {
      async function getMoviesWithId() {
        try {
          const res = await fetch(
            `https://homely-mia-hng-c4ac2199.koyeb.app/movies/${searchId}`
          );
          const data = await res.json();

          console.log(data);

          setMoviesData(data);
        } catch (error) {
          console.log(error.message);
        }
      }

      getMoviesWithId();
    },
    [searchId]
  );

  return (
    <section className="flex flex-col h-screen">
      <nav className="flex items-center gap-[2rem] px-[3rem] py-[1.5rem]">
        <figure className="text-[2.5rem] text-white font-semibold bg-orange-700 p-[1rem] rounded-lg">
          <Link to="/">M</Link>
        </figure>
        <p className="flex flex-col">
          <span className="text-[2rem] font-semibold">{title}</span>
          <span className="text-[1.3rem]">{tagline}</span>
        </p>
      </nav>

      <div className="h-auto flex items-center justify-center gap-[2rem] p-[3rem]">
        <div className="w-[80%] h-full flex flex-col gap-[1rem]">
          <div className="w-full h-[40rem] mb-[2rem]">
            {trailer && (
              <iframe
                src={`https://www.youtube.com/embed/${new URL(
                  trailer
                ).searchParams.get("v")}`}
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
                title="Movie Trailer"
                className="block w-full h-full"
              ></iframe>
            )}
          </div>
          <p>
            <span className="font-bold text-[2rem] text-orange-700">
              Description:
            </span>
            <span className="text-[1.6rem]"> {description}</span>
          </p>
          <p>
            <span className="font-bold text-[2rem] text-orange-700">
              Release Date:
            </span>
            <span className="text-[1.6rem]"> {releaseDate}</span>
          </p>
          <p>
            <span className="font-bold text-[2rem] text-orange-700 block mb-[.5rem]">
              Starring:
            </span>
            <span className="flex flex-wrap gap-[.25rem] text-[1.6rem]">
              {starring &&
                starring.map(({ name }) => (
                  <li key={name} className="list-none">
                    {name},
                  </li>
                ))}
            </span>
          </p>
        </div>
        <aside className="flex-1 h-full flex flex-col gap-4">
          <h4 className="text-[2rem] font-semibold">Genre</h4>
          <ul className="text-[1.6rem] flex flex-col gap-3">
            {genres &&
              genres.map((genre) => (
                <li
                  key={genre}
                  className="px-[2rem] py-[.5rem] bg-orange-700 text-white rounded-3xl"
                >
                  {genre}
                </li>
              ))}
          </ul>
          <button className="block mt-auto bg-orange-700 p-4 text-[1.5rem] text-white font-bold rounded-2xl">
            Book Movie Ticket
          </button>
        </aside>
      </div>
    </section>
  );
}

export default MovieDetails;
