/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

/* 
 * File:   Localization.h
 * Author: lila7
 *
 * Created on 22. November 2016, 12:35
 */

#ifndef LOCALIZATION_H
#define LOCALIZATION_H

class POMDPMCLocalization {
    static int running;
    static double epsilon;
public:
    POMDPMCLocalization();
    POMDPMCLocalization(const POMDPMCLocalization& orig);
    virtual ~POMDPMCLocalization();
    int POMDPMCLocalization::Search(std::list h);
    int POMDPMCLocalization::Rollout(State s, std::list list, int depth);
    int POMDPMCLocalization::Simulate(State s, std::list h, int depth);
private:

};

#endif /* LOCALIZATION_H */

