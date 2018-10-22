import { Component, OnInit } from "@angular/core";
import { AuthService } from "./../auth.service";

@Component({
  selector: "app-user-dashboard",
  templateUrl: "./user-dashboard.component.html",
  styleUrls: ["./user-dashboard.component.css"]
})
export class UserDashboardComponent implements OnInit {
  isLoggedIn: boolean = false;
  username: string = 'not defined';

  constructor(private auth: AuthService) {}

  ngOnInit(): void {
    const access_token = localStorage.getItem("access_token");
    if (access_token) {
      this.auth
        .ensureAuthenticated(access_token)
        .then(user => {
          console.log("LoggerUser Get Status", user.status);
          if (user.status == "200") {
            this.isLoggedIn = true;
            this.username = user.json().username;
          }
        })
        .catch(err => {
          console.log(err);
        });
    }
  }
}