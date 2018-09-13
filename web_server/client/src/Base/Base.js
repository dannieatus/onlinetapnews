import 'materialize-css/dist/css/materialize.min.css';
import 'materialize-css/dist/js/materialize.min.js';

import React from 'react';
import App from '../App/App';
import Auth from '../Auth/Auth';
import LoginPage from '../Login/LoginPage';
import SignUpPage from '../SignUp/SignUpPage';
import AboutUs from '../AboutUs/AboutUs';
import { BrowserRouter as Router, Route, Link, withRouter } from 'react-router-dom';

import './Base.css';


const logout = (history) => {
  Auth.deauthenticateUser();
  history.push('/login');
};

// withrouter: router is a kuangjia component, so use withRouter{}
// browser history
const Base = withRouter(({ history }) => (
  <div>
    <nav className="nav-bar indigo lightnen-1">
      <div className="nav-wrapper">
        <a href="/" className="brand-logo">Tap News</a>
        <ul id='nav-mobile' className='right'>
          {Auth.isUserAuthenticated() ? 
            (<div>
              <li><Link to="/aboutus">About us</Link></li>
              <li>{Auth.getEmail()}</li>
              <li><a onClick={()=>{logout(history);}}>Log out</a></li>
            </div>)
            :
            (<div>
              <li><Link to="/aboutus">About us</Link></li>
              <li><Link to="/login">Log in</Link></li>
              <li><Link to="/signup">Sign up</Link></li>
            </div>)
          }
        </ul>
      </div>
    </nav>
    <br/>
    <Route exact path="/" render={() => (Auth.isUserAuthenticated() ?
      (<App />) : <LoginPage />)} />
    <Route exact path="/login" component={LoginPage} />
    <Route exact path="/signup" component={SignUpPage} />
    <Route exact path="/aboutus" component={AboutUs} />
  </div>
));

export default Base;