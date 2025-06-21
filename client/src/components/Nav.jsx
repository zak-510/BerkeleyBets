import { Link } from "react-router";
import CalLogo from "../assets/callogo.png";

const Nav = () => {
  return (
    <div className="w-full flex items-center border-b">
      <div className="p-5 max-w-5xl w-full flex justify-between">
        <div className="flex justify-between gap-5">
          <img className="w-10 object-contain" src={CalLogo}></img>
          <Link
            className="text-4xl font-instrument-serif text-yellow-500"
            to="/"
          >
            BerkeleyBets
          </Link>
        </div>
        <div className="flex justify-between gap-5 items-center">
          <Link to="/log-in">Log in</Link>
          <Link to="/sign-up">Sign up</Link>
        </div>
      </div>
    </div>
  );
};

export default Nav;
