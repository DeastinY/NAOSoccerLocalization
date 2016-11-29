/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

/* 
 * File:   Localization.cpp
 * Author: lschulzedephoff
 * 
 * Created on 22. November 2016, 12:35
 */

#include <list>

#include "POMDPMCLocalization.h"

POMDPMCLocalization::POMDPMCLocalization() {
    running = true;
    epsilon = 0.2;
    gamma = 0.2;
    s = 0;
}

POMDPMCLocalization::POMDPMCLocalization(const POMDPMCLocalization& orig) {
}

POMDPMCLocalization::~POMDPMCLocalization() {
}

int POMDPMCLocalization::Search(std::list h){
   while(running){
        if(h.empty()){
            s = 1/h.size();
        }else{
            s = 0;//should be ~ B(h) - TODO
        }
        POMDPMCLocalization::Simulate(s, h, 0);
    }    
    return 0;//should be argmax V(hb) -TODO
}

int POMDPMCLocalization::Rollout(State s, std::list h, int depth){
    if(std::pow(gamma,depth) < epsilon){
        return 0;
    }
/*
a ~ PIrollout(h,.)
(s1, o, r) ~ G(s, a)
return r + Rollout(s1, hao, depth+1);*/
}

int POMDPMCLocalization::Simulate(State s, std::list h, int depth){
    if(std::pow(gamma,depth) < epsilon){
        return 0;
    }
  /*
    if(h != T){
        for(all a from A ){
            T(ha)<--(Ninit(ha), Vinit(ha),null);
        }
        return POMDPMCLocalization::Rollout(s, h, depth);
    }
    a<--argmax V(hb) + c sqrt(logN(h)/N(hb))
    (s1; o; r) ~ G(s; a)
    R<-- r + POMDPMCLocalization::Simulate(s0, hao, depth + 1);
    B(h)<--B(h) U {s}
    N(h)<-- N(h) + 1
    N(ha)<-- N(ha) + 1
    V (ha) <--  V (ha) + (R-V(ha)/N(ha))
    return R;
  * */
}

int POMDPMCLocalization::Rollout(State s, std::list h, int depth){
/*    if(gamma(depth) < epsilon){
        return 0;
    }
a ~ PIrollout(h,.)
(s', o, r) ~ G(s, a)
return r + Rollout(s', hao, depth+1);*/
}

int POMDPMCLocalization::Simulate(State s, std::list h, int depth){
 /*   if(gamma(depth) < epsilon){
        return 0;
    }
    if(h != T){
        for(all a from A ){
            T(ha)<--(Ninit(ha), Vinit(ha),null);
        }
        return Localization::Rollout(s, h, depth);
    }
    a<--argmax V(hb) + c sqrt(logN(h)/N(hb))
    (s0; o; r) ~ G(s; a)
    R<-- r + Localization::Simulate(s0, hao, depth + 1);
    B(h)<--B(h) U {s}
    N(h)<-- N(h) + 1
    N(ha)<-- N(ha) + 1
    V (ha) <--  V (ha) + (R-V(ha)/N(ha))
    return R;
  * */
}
