import { useState } from "react";
import { Link, useParams } from "react-router-dom";

function Signup() {
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [password, setPassword] = useState("");
  const [email, setEmail] = useState("");

  const { id, theater } = useParams();

  async function handleSubmit(e) {
    e.preventDefault();
    try {
      const res = await fetch(
        "https://homely-mia-hng-c4ac2199.koyeb.app/auth/user/signup",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            first_name: firstName,
            last_name: lastName,
            password: password,
            email: email,
          }),
        }
      );

      const text = await res.text();
      const data = text ? JSON.parse(text) : {};

      sessionStorage.setItem("accessToken", JSON.stringify(data.access_token));
      localStorage.setItem("refreshToken", JSON.stringify(data.refresh_token));
    } catch (error) {
      console.log(error.message);
    }
  }

  return (
    <section className="absolute top-0 left-0 w-full h-full bg-black bg-opacity-80 flex items-center justify-center">
      <form
        action=""
        className="w-[40%] h-auto bg-gray-50 flex flex-col items-center justify-center gap-[3rem] rounded-[1rem] py-[2rem]"
        onSubmit={handleSubmit}
      >
        <figure className="flex items-center justify-center gap-[1rem] h-auto">
          <Link
            to="/"
            className="text-[2.5rem] text-white font-semibold bg-orange-700 py-[.3rem] px-[1rem] rounded-lg"
          >
            M
          </Link>
          <p className="font-bold leading-10 text-orange-700 text-[3rem]">
            Movy
          </p>
        </figure>

        <div className="flex-1 px-[4rem] text-[1.4rem] w-full flex flex-col gap-[2rem]">
          <div className="flex flex-col items-start gap-[.5rem]">
            <label htmlFor="firstname">First Name</label>
            <input
              type="text"
              id="firstname"
              placeholder="Enter first name"
              className="w-full px-[2rem] py-[1rem] outline-none rounded-[4rem] border-[1.8px] border-orange-400"
              onChange={(e) => setFirstName(e.target.value)}
            />
          </div>
          <div className="flex flex-col items-start gap-[.2rem]">
            <label htmlFor="lastname">Last Name</label>
            <input
              type="text"
              id="lastname"
              placeholder="Enter last name"
              className="w-full px-[2rem] py-[1rem] outline-none rounded-[4rem] border-[1.8px] border-orange-400"
              onChange={(e) => setLastName(e.target.value)}
            />
          </div>
          <div className="flex flex-col items-start gap-[.2rem]">
            <label htmlFor="email">Email</label>
            <input
              type="email"
              id="email"
              placeholder="Enter first name"
              className="w-full px-[2rem] py-[1rem] outline-none rounded-[4rem] border-[1.8px] border-orange-400"
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>
          <div className="flex flex-col items-start gap-[.2rem]">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              placeholder="Enter password"
              className="w-full px-[2rem] py-[1rem] outline-none rounded-[4rem] border-[1.8px] border-orange-400"
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>
          <button className="bg-orange-700 text-white font-semibold mt-[1.5rem] py-[1rem] rounded-[4rem]">
            Create Account
          </button>
        </div>

        <p className="text-[1.5rem]">
          Already have an account{" "}
          <Link
            to={`/${id}/${theater}/signin`}
            className="underline text-orange-700"
          >
            Login
          </Link>
        </p>
      </form>
    </section>
  );
}

export default Signup;
