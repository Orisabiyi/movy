import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

function Theater() {
  const [theater, setTheater] = useState([]);
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

          console.log(data.theatres);
        } catch (error) {
          console.log(error);
        }
      }

      getTheaters();
    },
    [id]
  );

  return <section>Hello Theater</section>;
}

export default Theater;
