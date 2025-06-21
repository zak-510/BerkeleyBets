import { Link } from "react-router";
import CalLogo from "../assets/callogo.png";
import { useContext } from "react";
import { getAuth, signOut } from "firebase/auth";
import { Context } from "..";

const Nav = () => {
  const ctx = useContext(Context);
  const auth = getAuth();

  return (
    <div className=" index w-full flex items-center border-b border-white/25">
      <div className=" z-50 p-5 max-w-5xl w-full flex justify-between">
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
          {!ctx.user ? (
            <>
              <Link to="/log-in">Log in</Link>
              <Link to="/sign-up">Sign up</Link>
            </>
          ) : (
            <>
              <div className="flex flex-col items-center">
                <p className="text-xs">Bear Bucks</p>
                <p className="text-xl">0</p>
              </div>
              <button
                onClick={() => {
                  signOut(auth);
                }}
              >
                Log out
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default Nav;
