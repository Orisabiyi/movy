import { Link } from "react-router-dom";

function Navbar() {
  return (
    <nav className="flex justify-between absolute top-[2rem] left-[50%] translate-x-[-50%] z-[12] w-[95%] px-[2rem] py-[1rem] rounded-[1rem] text-[3rem] text-white">
      <h1 className="font-semibold">
        <Link to="/">MOVY</Link>
      </h1>
      <input
        type="text"
        name="user-search"
        className="px-[1.5rem] py-[.5rem] outline-none w-[45%] text-[1.8rem] rounded-[50rem] bg-slate-400 bg-opacity-35"
      />
      <div>Filter</div>
    </nav>
  );
}

export default Navbar;
