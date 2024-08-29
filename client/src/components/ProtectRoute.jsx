import PropTypes from "prop-types";
import { useNavigate } from "react-router-dom";

function ProtectRoute({ children }) {
  const navigate = useNavigate("");
  if (
    !sessionStorage.getItem("accessToken") &&
    !localStorage.getItem("refreshToken")
  )
    return navigate(-1);

  return <>{children}</>;
}

ProtectRoute.propTypes = {
  children: PropTypes.node.isRequired,
};

export default ProtectRoute;
