import Navbar from "../components/Navbar";
import Carousel from "../components/Carousel";
import "./Homepage.style.css";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

function App() {
  const [displayMovies, setDisplayMovies] = useState([]);

  useEffect(function () {
    async function displayMovies() {
      const res = await fetch(
        "https://homely-mia-hng-c4ac2199.koyeb.app/?page=1&size=30"
      );
      const data = await res.json();
      setDisplayMovies(data.results);
    }

    displayMovies();
  }, []);

  return (
    <>
      <header className="h-[100vh] relative flex items-center justify-center">
        <Navbar />
        <div className="overlay absolute w-full h-full z-10"></div>
        <Carousel />
      </header>

      <section className="grid grid-cols-3 px-[6rem] py-[10rem] gap-[3rem] bg-slate-300">
        {displayMovies.map(
          ({
            id,
            title,
            description,
            poster_path: posterPath,
            release_date: releaseDate,
          }) => (
            <figure
              key={title}
              className="flex flex-col h-auto border-[.2rem] rounded-b-[1.5rem]"
            >
              <div className="h-[60%]">
                <img src={posterPath} alt={title} className="w-full h-full" />
              </div>
              <div className="p-[1.8em] flex flex-col gap-[.5rem] flex-1">
                <h3 className="text-[1.8rem] font-semibold">{title}</h3>
                <p className="text-[1.3rem]">Release Date: {releaseDate}</p>
                <p className="text-[1.3rem]">Description: {description}</p>

                <div className="mt-auto text-[1.5rem] font-semibold text-blue-950 underline">
                  <Link to={`${title.replace(":", "")}?${id}`}>
                    Check Movie Full Details
                  </Link>
                </div>
              </div>
            </figure>
          )
        )}
      </section>
    </>
  );
}

export default App;
