// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./MAIA.sol";

contract DAO {
    MAIA public maiaToken;
    
    struct Proposal {
        string description;
        uint256 voteCount;
        bool executed;
    }
    
    Proposal[] public proposals;
    mapping(address => bool) public hasVoted;
    
    constructor(address _maiaToken) {
        maiaToken = MAIA(_maiaToken);
    }
    
    function createProposal(string memory _description) public {
        proposals.push(Proposal({
            description: _description,
            voteCount: 0,
            executed: false
        }));
    }
    
    function vote(uint256 _proposalId) public {
        require(!hasVoted[msg.sender], "Already voted");
        require(maiaToken.transferFrom(msg.sender, address(this), 1 * 10**maiaToken.decimals()), "Transfer failed");
        
        proposals[_proposalId].voteCount += 1;
        hasVoted[msg.sender] = true;
    }
    
    function executeProposal(uint256 _proposalId) public {
        require(!proposals[_proposalId].executed, "Already executed");
        proposals[_proposalId].executed = true;
    }
}